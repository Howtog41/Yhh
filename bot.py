import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF for handling text, images, layers

# Load bot token from environment variable for security
BOT_TOKEN = os.getenv('5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4')

# Function to start the bot
async def start(update: Update, context) -> None:
    await update.message.reply_text("Send me a PDF file, and I will attempt to remove the watermark.")

# Function to handle PDF file
async def handle_pdf(update: Update, context) -> None:
    pdf_file = update.message.document
    if pdf_file.mime_type != 'application/pdf':
        await update.message.reply_text("Please upload a valid PDF file.")
        return

    file_id = pdf_file.file_id
    file = await context.bot.get_file(file_id)
    file_path = f"{file_id}.pdf"
    await file.download_to_drive(file_path)

    # Process PDF to remove watermarks
    try:
        output_pdf = f"output_{file_id}.pdf"
        watermark_text = "Confidential"  # Change this to the watermark text you want to remove
        remove_watermark(file_path, output_pdf, watermark_text)
        await update.message.reply_document(document=open(output_pdf, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"Could not remove the watermark: {e}")
    finally:
        # Clean up files after processing
        os.remove(file_path)
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

# Function to remove watermark from a PDF file
def remove_watermark(input_pdf, output_pdf, watermark_text=None):
    # Open the PDF using PyMuPDF (fitz)
    doc = fitz.open(input_pdf)

    # Process each page to remove text-based and image-based watermarks
    for page in doc:
        # 1. Remove text-based watermarks
        if watermark_text:
            text_instances = page.search_for(watermark_text)
            for inst in text_instances:
                page.add_redact_annot(inst, fill=(255, 255, 255))  # White fill to erase text
            page.apply_redactions()

        # 2. Remove image-based watermarks
        image_list = page.get_images(full=True)
        for img in image_list:
            # Deleting all images (assuming they are watermarks)
            xref = img[0]
            page.delete_image(xref)

        # 3. Remove semi-transparent watermarks
        for img in image_list:
            if page.get_image_info(img[0]).get('transparency'):
                xref = img[0]
                page.delete_image(xref)

        # 4. Remove layer-based watermarks (Optional Content Groups)
        ocgs = page.get_ocgs()
        if ocgs:
            page.set_ocg_visibility(ocgs, visible=False)  # Hides layers with watermarks

    # Save the processed file to a temporary output file
    temp_output = "temp_no_watermarks.pdf"
    doc.save(temp_output)
    doc.close()

    # 5. Remove metadata watermarks using PyPDF2
    reader = PdfReader(temp_output)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Clear metadata
    writer.add_metadata({})

    with open(output_pdf, "wb") as final_output:
        writer.write(final_output)

    # Clean up the temporary file
    os.remove(temp_output)

# Main function to run the bot
def main():
    # Create the Application instance using the bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
