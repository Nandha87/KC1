import sys
import polars as pl
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import io
import base64
import flet as ft
import speech_recognition as sr
from flet import Page, Text, TextField, ElevatedButton, Row, Image, GridView, MainAxisAlignment, FontWeight
from communication import TouchSensor

# DatasetAnalyzer class to handle data loading and preprocessing
class DatasetAnalyzer:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.data = None
        self.pandas_data = None

    def load_data(self):
        try:
            if self.dataset_name.endswith('.csv'):
                self.data = pl.read_csv(self.dataset_name)
            elif self.dataset_name.endswith('.xlsx') or self.dataset_name.endswith('.xls'):
                self.data = pl.read_excel(self.dataset_name)
            else:
                seaborn_data = sns.load_dataset(self.dataset_name)
                self.data = pl.DataFrame(seaborn_data)
            print(f"Data loaded: {self.dataset_name}")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def preprocess_data(self):
        try:
            numerical_cols = [col for col in self.data.columns if self.data[col].dtype in (pl.Float64, pl.Int64)]
            categorical_cols = [col for col in self.data.columns if self.data[col].dtype == pl.Utf8]
            for col in numerical_cols:
                self.data = self.data.with_columns(pl.col(col).fill_null(self.data[col].mean()))
            for col in categorical_cols:
                self.data = self.data.with_columns(pl.col(col).fill_null("missing"))
            scaler = StandardScaler()
            for col in numerical_cols:
                scaled_values = scaler.fit_transform(self.data[col].to_numpy().reshape(-1, 1))
                self.data = self.data.with_columns(pl.Series(col, scaled_values.flatten()))
            self.pandas_data = self.data.to_pandas()
            print("Data preprocessing completed.")
        except Exception as e:
            print(f"Error during preprocessing: {e}")
            raise

    def calculate_correlation(self):
        try:
            numerical_cols = [col for col in self.data.columns if self.data[col].dtype in (pl.Float64, pl.Int64)]
            if len(numerical_cols) < 2:
                raise ValueError("At least two numerical columns are required for correlation calculation.")
            numerical_data = self.data.select(numerical_cols).to_numpy()
            corr_matrix = np.corrcoef(numerical_data, rowvar=False)
            print("Correlation matrix calculated.")
            return corr_matrix, numerical_cols
        except Exception as e:
            print(f"Error calculating correlation: {e}")
            raise

    def find_highest_correlation(self, corr_matrix, numerical_cols):
        try:
            abs_corr_matrix = np.abs(corr_matrix)
            np.fill_diagonal(abs_corr_matrix, 0)
            max_corr = np.unravel_index(np.argmax(abs_corr_matrix), abs_corr_matrix.shape)
            col1, col2 = numerical_cols[max_corr[0]], numerical_cols[max_corr[1]]
            print(f"Highest correlation: {col1} and {col2}")
            return col1, col2
        except Exception as e:
            print(f"Error finding highest correlation: {e}")
            raise

# Helper function to convert Matplotlib figures to base64
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64

# Plot generation functions
def generate_heatmap(corr_matrix, numerical_cols):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax, cbar=True)
    ax.set_xticklabels(numerical_cols, rotation=45)
    ax.set_yticklabels(numerical_cols, rotation=0)
    ax.set_title("Correlation Heatmap")
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    return img_base64

def generate_scatter_plot(data, col1, col2, correlation):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.regplot(x=data[col1], y=data[col2], ax=ax)
    ax.set_xlabel(f"{col1} (standardized)")
    ax.set_ylabel(f"{col2} (standardized)")
    ax.set_title(f"Scatter Plot of {col1} vs {col2}\nCorrelation: {correlation:.2f}")
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    return img_base64

def generate_histogram(data, col):
    fig, ax = plt.subplots(figsize=(6, 4))  # Increased size to prevent label cropping
    sns.histplot(data[col], kde=True, ax=ax)
    ax.set_title(f"Histogram of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    fig.tight_layout()  # Adjust layout to prevent cropping
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    return img_base64

def generate_count_plot(data, col):
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.countplot(x=col, data=data, ax=ax)
    ax.set_title(f"Count Plot of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    ax.tick_params(axis='x', rotation=45)
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    return img_base64

def generate_pie_chart(data, col):
    fig, ax = plt.subplots(figsize=(4, 4))
    counts = data[col].value_counts()
    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title(f"Pie Chart of {col}")
    img_base64 = fig_to_base64(fig)
    plt.close(fig)
    return img_base64

# Flet app main function
def main(page: ft.Page):
    page.title = "Dataset Dashboard"
    page.scroll = "auto"
    page.full_screen = True

    # Initialize touch sensor
    touch_sensor = TouchSensor()
    
    # Keep track of current dataset and graph index
    current_dataset = None
    current_graph_index = 0
    graph_items = []  # Will store all graph items
    
    def handle_touch(sensor):
        """Handle touch events from different sensors"""
        if sensor == "CS1" and current_dataset:  # CS1: Reload current dataset
            page.add(ft.Text("Touch detected on CS1! Reloading current dataset...", size=16))
            load_dashboard(current_dataset)
        elif sensor == "CS2":  # CS2: Next graph
            if graph_items:
                nonlocal current_graph_index
                if current_graph_index < len(graph_items) - 1:
                    current_graph_index += 1
                    update_current_graph()
                    page.add(ft.Text("Moving to next graph...", size=14))
        elif sensor == "CS3":  # CS3: Previous graph
            if graph_items:
                nonlocal current_graph_index
                if current_graph_index > 0:
                    current_graph_index -= 1
                    update_current_graph()
                    page.add(ft.Text("Moving to previous graph...", size=14))
    
    # Set up touch sensor callback
    touch_sensor.set_touch_callback(handle_touch)
    touch_sensor.start_monitoring()

    # Function to display the centered input screen
    def show_input_screen():
        page.clean()  # Clear the current page content
        dataset_input = ft.TextField(label="Enter dataset name", width=300)
        load_button = ft.ElevatedButton("Load Dashboard", on_click=lambda e: load_dashboard(dataset_input.value))
        # Center the input box and button horizontally
        input_row = ft.Row([dataset_input, load_button], alignment=ft.MainAxisAlignment.CENTER)
        page.add(ft.Text("Enter the name of the dataset you want to analyze:", size=16), input_row)
        page.add(ft.Text("Touch Controls:", size=14, weight=ft.FontWeight.BOLD))
        page.add(ft.Text("• CS1: Reload current dataset", size=14, color="gray"))
        page.add(ft.Text("• CS2: Next graph", size=14, color="gray"))
        page.add(ft.Text("• CS3: Previous graph", size=14, color="gray"))

    def update_current_graph():
        """Update the current graph display"""
        if graph_items and 0 <= current_graph_index < len(graph_items):
            title_text.value = graph_items[current_graph_index][0]
            graph_image.src_base64 = graph_items[current_graph_index][1]
            title_text.update()
            graph_image.update()

    # Function to load and display the dashboard
    def load_dashboard(dataset_name):
        if not dataset_name.strip():
            page.add(ft.Text("Please enter a dataset name."))
            return

        try:
            # Store current dataset name
            nonlocal current_dataset
            current_dataset = dataset_name

            # Initialize and process data
            analyzer = DatasetAnalyzer(dataset_name)
            analyzer.load_data()
            analyzer.preprocess_data()
            corr_matrix, numerical_cols = analyzer.calculate_correlation()
            col1, col2 = analyzer.find_highest_correlation(corr_matrix, numerical_cols)

            # Generate plots as base64 images
            heatmap_img = generate_heatmap(corr_matrix, numerical_cols)
            scatter_img = generate_scatter_plot(
                analyzer.pandas_data, col1, col2,
                corr_matrix[numerical_cols.index(col1), numerical_cols.index(col2)]
            )
            histogram_imgs = [generate_histogram(analyzer.pandas_data, col) for col in numerical_cols]
            categorical_cols = [col for col in analyzer.pandas_data.columns if analyzer.pandas_data[col].dtype == 'object']
            count_plot_imgs = [generate_count_plot(analyzer.pandas_data, col) for col in categorical_cols]
            pie_cols = [col for col in categorical_cols if analyzer.pandas_data[col].nunique() <= 5]
            pie_chart_imgs = [generate_pie_chart(analyzer.pandas_data, col) for col in pie_cols]

            # Clear previous content
            page.clean()

            # Back button
            back_button = ft.ElevatedButton("Back", on_click=lambda e: show_input_screen())

            # Combine all images with titles into one list
            nonlocal graph_items
            graph_items = [
                ("Correlation Heatmap", heatmap_img),
                ("Scatter Plot", scatter_img)
            ] + [(f"Histogram of {col}", img) for col, img in zip(numerical_cols, histogram_imgs)] + [(f"Count Plot of {col}", img) for col, img in zip(categorical_cols, count_plot_imgs)] + [(f"Pie Chart of {col}", img) for col, img in zip(pie_cols, pie_chart_imgs)]

            current_graph_index = 0
            title_text = ft.Text(graph_items[current_graph_index][0], size=20, weight=ft.FontWeight.BOLD)
            graph_image = ft.Image(src_base64=graph_items[current_graph_index][1], width=600, height=600)

            # Add touch control instructions
            page.add(ft.Text("Touch Controls:", size=14, weight=ft.FontWeight.BOLD))
            page.add(ft.Text("• CS1: Reload current dataset", size=14, color="gray"))
            page.add(ft.Text("• CS2: Next graph", size=14, color="gray"))
            page.add(ft.Text("• CS3: Previous graph", size=14, color="gray"))

            nav_buttons = Row([ElevatedButton("Previous", on_click=prev_graph), ElevatedButton("Next", on_click=next_graph)], alignment=MainAxisAlignment.CENTER)

            page.add(back_button, title_text, graph_image, nav_buttons)

            # Voice Command for Navigation
            def voice_command():
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Listening for voice command... Speak 'Next' or 'Previous'.")
                    audio = recognizer.listen(source)

                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Voice Command: {command}")

                    if "next" in command:
                        next_graph(None)
                    elif "previous" in command:
                        prev_graph(None)
                except sr.UnknownValueError:
                    print("Could not understand the audio")
                except sr.RequestError:
                    print("Could not request results from Google Speech Recognition service")

            # Call the voice command function periodically
            import threading
            def listen_for_voice():
                while True:
                    voice_command()

            threading.Thread(target=listen_for_voice, daemon=True).start()

        except Exception as e:
            page.add(ft.Text(f"Error: {e}"))

    # Show input screen initially
    show_input_screen()

    # Clean up when the page is closed
    def on_close(e):
        touch_sensor.stop_monitoring()
        page.window_destroy()

    page.on_window_event = on_close

# Run the Flet app
ft.app(target=main)
