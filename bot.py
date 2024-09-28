from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import fitz  # PyMuPDF

# PDF se watermark ko remove karne ka function
def remove_watermark(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        # Watermark ko remove karne ke liye text box ya image ko identify karna
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    if "watermark" in s["text"].lower():
                        page.delete_textblock(b)
    doc.save(output_path)

# Bot ke zariye PDF file ko handle karna
async def handle_pdf(update: Update, context):
    file = await update.message.document.get_file()
    await file.download_to_drive("input.pdf")

    remove_watermark("input.pdf", "output.pdf")

    await context.bot.send_document(chat_id=update.message.chat_id, document=open("output.pdf", "rb"))

# Telegram bot setup
async def main():
    application = Application.builder().token("5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4").build()

    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Application ko run_polling ke saath start karte hain
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
