import os
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid Tkinter issues
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import textwrap
from uuid import uuid4
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.units import inch

def wrap_labels(labels, width=20):
    """Wrap long labels to fit within the plot."""
    return [textwrap.fill(label, width=width) for label in labels]

def generate_charts(data, asset_name='test.com'):
    # Create folder to store charts
    folder_name = str(uuid4())
    folder_path = os.path.join(settings.MEDIA_ROOT, 'chart', folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Convert data to DataFrame
    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    if df.empty:
        raise ValueError("DataFrame is empty after dropping duplicates.")

    # Draw pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(df['count'], labels=df['vulnerability_type'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Distribution of Vulnerabilities by Type', fontsize=16)
    plt.tight_layout()
    pie_chart_path = os.path.join(folder_path, 'pie_chart.png')
    plt.savefig(pie_chart_path, dpi=300)
    plt.close()

    # Draw heatmap
    plt.figure(figsize=(8, 6))
    severity_order = ['Low', 'Medium', 'High', 'Critical']
    heatmap_data = df.pivot(index='vulnerability_type', columns='severity', values='count').reindex(columns=severity_order)
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap='coolwarm', cbar_kws={'label': 'Number of Vulnerabilities'})
    plt.title('Vulnerability Count by Type and Severity', fontsize=16)
    plt.tight_layout()
    heatmap_path = os.path.join(folder_path, 'heatmap.png')
    plt.savefig(heatmap_path, dpi=300)
    plt.close()

    # Draw area chart
    time_df = df.groupby('vulnerability_type').sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.fill_between(time_df['vulnerability_type'], time_df['count'], color='skyblue', alpha=0.4)
    plt.plot(time_df['vulnerability_type'], time_df['count'], color='Slateblue', alpha=0.6)
    plt.title('Area Chart of Vulnerabilities by Type', fontsize=16)
    plt.xlabel('Vulnerability Type', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    area_chart_path = os.path.join(folder_path, 'area_chart.png')
    plt.savefig(area_chart_path, dpi=300)
    plt.close()

    # Draw box plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='vulnerability_type', y='severity', data=df, palette='coolwarm')
    plt.title('Box Plot of Vulnerability Severity by Type', fontsize=16)
    plt.xlabel('Vulnerability Type', fontsize=14)
    plt.ylabel('Severity', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    box_plot_path = os.path.join(folder_path, 'box_plot.png')
    plt.savefig(box_plot_path, dpi=300)
    plt.close()

    # Draw bar chart
    plt.figure(figsize=(12, 8))
    wrapped_labels = wrap_labels(df['vulnerability_type'])
    sns.barplot(x=wrapped_labels, y='count', data=df, hue='vulnerability_type', palette='viridis', dodge=False)
    plt.title('Number of Vulnerabilities by Type', fontsize=16)
    plt.xlabel('Vulnerability Type', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.xticks(rotation=90, ha='right')
    plt.legend([], [], frameon=False)
    plt.tight_layout()
    bar_chart_path = os.path.join(folder_path, 'bar_chart.png')
    plt.savefig(bar_chart_path, dpi=300)
    plt.close()

    # Return folder path
    return os.path.join('chart', folder_name)


def create_pdf_with_images(image_paths):
    # Create a temporary file to store the PDF
    temp_pdf = NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf_path = temp_pdf.name
    temp_pdf.close()  # Close the file so reportlab can write to it

    # Create a PDF canvas
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    width, height = letter

    # Define starting position for images
    x = 0.5 * inch
    y = height - 1 * inch

    for image_path in image_paths:
        # Open an image file
        with Image.open(image_path) as img:
            # Get image dimensions
            img_width, img_height = img.size
            # Convert pixels to points (1 inch = 72 points)
            img_width_points = img_width * 72 / img.info['dpi'][0]
            img_height_points = img_height * 72 / img.info['dpi'][1]

            # Adjust image size if it's too large to fit on the page
            max_width = width - 1 * inch
            max_height = height - 2 * inch

            if img_width_points > max_width:
                scale_factor = max_width / img_width_points
                img_width_points = max_width
                img_height_points *= scale_factor

            if img_height_points > max_height:
                scale_factor = max_height / img_height_points
                img_height_points = max_height
                img_width_points *= scale_factor

            # Check if image fits on the page, otherwise add a new page
            if y - img_height_points < 0:
                c.showPage()
                c.setPageSize(letter)
                y = height - 1 * inch

            # Draw the image
            c.drawImage(image_path, x, y - img_height_points, width=img_width_points, height=img_height_points)
            y -= img_height_points + 0.5 * inch  # Move down for the next image

    # Save the PDF file
    c.save()

    return temp_pdf_path