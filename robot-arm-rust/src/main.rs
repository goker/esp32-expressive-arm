use clap::Parser;
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Parser)]
#[clap(version = "1.0", author = "Your Name")]
struct Opts {
    #[clap(subcommand)]
    subcmd: SubCommand,
}

#[derive(Parser)]
enum SubCommand {
    Do {
        prompt: String,
    },
}

#[derive(Serialize)]
struct GenerationConfig {
    temperature: f32,
    #[serde(rename = "topK")]
    top_k: u32,
    #[serde(rename = "topP")]
    top_p: f32,
    #[serde(rename = "maxOutputTokens")]
    max_output_tokens: u32,
}

#[derive(Serialize)]
struct RequestBody {
    contents: Vec<Content>,
    #[serde(rename = "generationConfig")]
    generation_config: GenerationConfig,
}

#[derive(Serialize)]
struct Content {
    parts: Vec<Part>,
}

#[derive(Serialize)]
struct Part {
    text: String,
}

#[derive(Deserialize)]
struct ResponseBody {
    candidates: Vec<Candidate>,
}

#[derive(Deserialize)]
struct Candidate {
    content: ContentResponse,
}

#[derive(Deserialize)]
struct ContentResponse {
    parts: Vec<PartResponse>,
}

#[derive(Deserialize)]
struct PartResponse {
    text: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts: Opts = Opts::parse();
    match opts.subcmd {
        SubCommand::Do { prompt } => {
            let api_key = std::env::var("GEMINI_API_KEY")
                .expect("GEMINI_API_KEY environment variable not set");

            let instructions = std::fs::read_to_string("../ai/AGENT_INSTRUCTIONS.md")?;

            let full_prompt = format!(
                "{}\n\n---\n\nUSER REQUEST: {}\n\nRemember: Return ONLY executable Python code.",
                instructions,
                prompt
            );

            let client = reqwest::Client::new();
            let response = client
                .post(format!(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={}",
                    api_key
                ))
                .json(&RequestBody {
                    contents: vec![Content {
                        parts: vec![Part { text: full_prompt }],
                    }],
                    generation_config: GenerationConfig {
                        temperature: 0.7,
                        top_k: 40,
                        top_p: 0.95,
                        max_output_tokens: 8192,
                    },
                })
                .send()
                .await?;

            let response_text = response.text().await?;
            let response_body: ResponseBody = serde_json::from_str(&response_text)?;
            let mut generated_code = response_body.candidates[0].content.parts[0].text.clone();

            // Clean up markdown if present
            if generated_code.starts_with("```python") {
                if let Some(start) = generated_code.find("```python") {
                    if let Some(end) = generated_code.rfind("```") {
                        generated_code = generated_code[start + 9..end].trim().to_string();
                    }
                }
            } else if generated_code.starts_with("```") {
                if let Some(start) = generated_code.find("```") {
                    if let Some(end) = generated_code.rfind("```") {
                        generated_code = generated_code[start + 3..end].trim().to_string();
                    }
                }
            }

            let demos_dir = std::path::Path::new("../demos");
            std::fs::create_dir_all(demos_dir)?; // Ensure the demos directory exists

            let mut next_num = 6;
            if let Ok(entries) = std::fs::read_dir(demos_dir) {
                let max_num = entries
                    .filter_map(Result::ok)
                    .map(|entry| entry.path())
                    .filter(|path| path.is_file())
                    .filter_map(|path| {
                        path.file_stem()
                            .and_then(|s| s.to_str())
                            .and_then(|s| s.split('_').next())
                            .and_then(|n| n.parse::<u32>().ok())
                    })
                    .max();

                if let Some(max) = max_num {
                    next_num = max + 1;
                }
            }

            let file_name = format!("{:02}_generated.py", next_num);
            let file_path = demos_dir.join(&file_name);

            std::fs::write(&file_path, &generated_code)?;

            println!("Generated script saved to {}", file_path.display());

            // Make the script executable
            use std::os::unix::fs::PermissionsExt;
            let mut perms = std::fs::metadata(&file_path)?.permissions();
            perms.set_mode(0o755);
            std::fs::set_permissions(&file_path, perms)?;

            let output = Command::new("python3")
                .current_dir("..")
                .arg(file_path.strip_prefix("../").unwrap())
                .output()?;

            println!("Script output:\n{}", String::from_utf8_lossy(&output.stdout));
            if !output.stderr.is_empty() {
                println!("Script error:\n{}", String::from_utf8_lossy(&output.stderr));
            }
        }
    }
    Ok(())
}