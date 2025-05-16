use std::fs;
use std::process;
fn main() {
    let path: &str = "/home/murakon/Synta_schedule.txt";
    let contents = match fs::read_to_string(path) {
        Ok(contents) => contents,
        Err(e) => {
            eprintln!("Error: {}", e);
            process::exit(1);
        },
    };

    println!("{}",&contents);
}
