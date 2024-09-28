import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PyPDF2 import PdfReader, PdfWriter

# Your bot token from BotFather
BOT_TOKEN = '5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4'

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
        remove_watermark(file_path, output_pdf)
        await update.message.reply_document(document=open(output_pdf, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"Could not remove the watermark: {e}")
    finally:
        os.remove(file_path)
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

# Function to remove watermark from a PDF file
def remove_watermark(input_pdf, output_pdf):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Simply copying pages without altering content for demo purposes
    for page in reader.pages:
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

# Main function to run the bot
def main():
    # Create the Application instance using the bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Start the bot (synchronous call)
    application.run_polling()

if __name__ == '__main__':
    main()
