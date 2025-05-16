use dirs::home_dir;
use std::fs;
use dioxus::prelude::*;

// main.css 
static CSS: Asset = asset!("/assets/main.css");
//script generated from Casy"
const FILE_PATH:&str=""; //Update file path
// eg const FILE_PATH:&str="Dev_prj/tele/teleprompter/script.txt"; //Update file path

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    rsx! {
        link { rel: "stylesheet", href: "{CSS}" }
        Content {}
    }
}

#[component]
fn Content() -> Element {
    let home=home_dir().expect("Home Directory not found");  //retrives home directory
    let full_path=home.join(FILE_PATH);// Joins the home directory with the path of the script. 
    let content = fs::read_to_string(&full_path).expect("Cannot read the file"); // Reads the file
    // and converts it into a string

    rsx! {
        div {
            id: "content",
            div {
            id: "scrolling-text",
            h1{"{content}"}
}
}
}
}
