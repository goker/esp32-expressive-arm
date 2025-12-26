use clap::Parser;
use serde::{Deserialize, Serialize};
use std::process::Command;

// Command-line argument parser configuration
#[derive(Parser)]
#[clap(version = "1.0", author = "Your Name")]
struct Opts {
    #[clap(subcommand)]
    subcmd: SubCommand,
}

#[derive(Parser)]
enum SubCommand {
    /// Generate and run a script from a text prompt
    Do {
        prompt: String,
    },
    /// Record 5 seconds of audio, transcribe it, and run as a prompt
    Listen,
}

// Structs for Gemini API request
#[derive(Serialize)]
struct GeminiGenerationConfig {
    temperature: f32,
    #[serde(rename = "topK")]
    top_k: u32,
    #[serde(rename = "topP")]
    top_p: f32,
    #[serde(rename = "maxOutputTokens")]
    max_output_tokens: u32,
}

#[derive(Serialize)]
struct GeminiRequestBody {
    contents: Vec<GeminiContent>,
    #[serde(rename = "generationConfig")]
    generation_config: GeminiGenerationConfig,
}

#[derive(Serialize)]
struct GeminiContent {
    parts: Vec<GeminiPart>,
}

#[derive(Serialize)]
struct GeminiPart {
    text: String,
}

// Structs for Gemini API response
#[derive(Deserialize)]
struct GeminiResponseBody {
    candidates: Vec<GeminiCandidate>,
}

#[derive(Deserialize)]
struct GeminiCandidate {
    content: GeminiContentResponse,
}

#[derive(Deserialize)]
struct GeminiContentResponse {
    parts: Vec<GeminiPartResponse>,
}

#[derive(Deserialize)]
struct GeminiPartResponse {
    text: String,
}

// Structs for OpenAI Whisper API response
#[derive(Deserialize)]
struct WhisperResponseBody {
    text: String,
}

/// Records 5 seconds of audio and transcribes it using OpenAI Whisper.
async fn record_and_transcribe() -> Result<String, Box<dyn std::error::Error>> {
    const AUDIO_FILE: &str = "output.wav";

    // --- 1. Record Audio ---
    println!("Recording for 5 seconds...");
    audio::record_audio(AUDIO_FILE, 5)?;
    println!("Recording complete.");

    // --- 2. Transcribe Audio ---
    println!("Transcribing audio...");
    let transcript = audio::transcribe_audio(AUDIO_FILE).await?;
    println!("Transcription complete.");
    Ok(transcript)
}

/// Generates a Python script using the Gemini API and executes it.
async fn generate_and_run_script(prompt: String) -> Result<(), Box<dyn std::error::Error>> {
    let api_key =
        std::env::var("GEMINI_API_KEY").expect("GEMINI_API_KEY environment variable not set");

    let instructions = std::fs::read_to_string("../ai/AGENT_INSTRUCTIONS.md")?;
    let full_prompt = format!(
        "{}

---\n
USER REQUEST: {}

Remember: Return ONLY executable Python code.",
        instructions,
        prompt
    );

    let client = reqwest::Client::new();
    let response = client
        .post(&format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={}",
            api_key
        ))
        .json(&GeminiRequestBody {
            contents: vec![GeminiContent {
                parts: vec![GeminiPart { text: full_prompt }],
            }],
            generation_config: GeminiGenerationConfig {
                temperature: 0.7,
                top_k: 40,
                top_p: 0.95,
                max_output_tokens: 8192,
            },
        })
        .send()
        .await?;

    let response_text = response.text().await?;
    let response_body: GeminiResponseBody = serde_json::from_str(&response_text)?;
    let mut generated_code = response_body.candidates[0].content.parts[0].text.clone();

    // Clean up markdown fences
    if generated_code.starts_with("```python") {
        generated_code = generated_code
            .strip_prefix("```python\n")
            .unwrap_or(&generated_code)
            .strip_suffix("\n```")
            .unwrap_or(&generated_code)
            .trim()
            .to_string();
    }

    // Save the script to the demos directory
    let demos_dir = std::path::Path::new("../demos");
    let next_num = (std::fs::read_dir(demos_dir)?
        .filter_map(Result::ok)
        .filter_map(|e| e.file_name().to_str()?.split('_').next()?.parse::<u32>().ok())
        .max()
        .unwrap_or(5)) 
        + 1;

    let file_name = format!("{:02}_generated.py", next_num);
    let file_path = demos_dir.join(&file_name);
    std::fs::write(&file_path, &generated_code)?;
    println!("Generated script saved to {}", file_path.display());

    // Make the script executable
    use std::os::unix::fs::PermissionsExt;
    let perms = std::fs::metadata(&file_path)?.permissions();
    let mut new_perms = perms.clone();
    new_perms.set_mode(0o755);
    std::fs::set_permissions(&file_path, new_perms)?;

    // Execute the script
    let output = Command::new("python3")
        .current_dir("..")
        .arg(file_path.strip_prefix("../").unwrap())
        .output()?;

    println!("Script output:\n{}", String::from_utf8_lossy(&output.stdout));
    if !output.stderr.is_empty() {
        eprintln!(
            "Script error:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    Ok(())
}

#[tokio::main] async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts: Opts = Opts::parse();
    match opts.subcmd {
        SubCommand::Do { prompt } => {
            generate_and_run_script(prompt).await?;
        }
        SubCommand::Listen => {
            let prompt = record_and_transcribe().await?;
            if !prompt.is_empty() {
                println!("Got prompt: \"{}\"", prompt);
                generate_and_run_script(prompt).await?;
            } else {
                println!("No speech detected or transcription failed.");
            }
        }
    }
    Ok(())
}

mod audio {
    use super::WhisperResponseBody;
    use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
    use hound;
    use reqwest::multipart;
    use std::fs::File;
    use std::io::{BufWriter, Read};
    use std::sync::{Arc, Mutex};
    pub fn record_audio(file_path: &str, duration_secs: u64) -> Result<(), Box<dyn std::error::Error>> {
        let host = cpal::default_host();
        let device = host.default_input_device().expect("no input device available");
        let config = device.default_input_config()?;
        let spec = hound::WavSpec {
            channels: config.channels() as u16,
            sample_rate: config.sample_rate().0,
            bits_per_sample: 16, // Typical for STT
            sample_format: hound::SampleFormat::Int,
        };

        let writer = hound::WavWriter::create(file_path, spec)?;
        let writer = Arc::new(Mutex::new(Some(writer)));

        let writer_clone = writer.clone();
        let stream = device.build_input_stream(
            &config.into(),
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                if let Some(writer) = writer_clone.lock().unwrap().as_mut() {
                    for &sample in data.iter() {
                        let sample = (sample * i16::MAX as f32) as i16;
                        writer.write_sample(sample).unwrap();
                    }
                }
            },
            |err| eprintln!("an error occurred on stream: {}", err),
            None
        )?;

        stream.play()?;
        std::thread::sleep(std::time::Duration::from_secs(duration_secs));
        drop(stream); // Stop the stream
        writer.lock().unwrap().take().unwrap().finalize()?;
        Ok(())
    }

    pub async fn transcribe_audio(file_path: &str) -> Result<String, Box<dyn std::error::Error>> {
        let mut audio_file = File::open(file_path)?;
        let mut audio_bytes = Vec::new();
        audio_file.read_to_end(&mut audio_bytes)?;

        let openai_api_key = std::env::var("OPENAI_API_KEY")
            .expect("OPENAI_API_KEY environment variable not set");

        let client = reqwest::Client::new();
        let form = multipart::Form::new()
            .part(
                "file",
                multipart::Part::bytes(audio_bytes).file_name(file_path.to_string()),
            )
            .text("model", "whisper-1");

        let response = client
            .post("https://api.openai.com/v1/audio/transcriptions")
            .header(
                "Authorization",
                format!("Bearer {}", openai_api_key),
            )
            .multipart(form)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(format!("OpenAI API Error: {}", error_text).into());
        }

        let response_body: WhisperResponseBody = response.json().await?;

        Ok(response_body.text)
    }
}
