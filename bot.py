from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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
                    # Yahan par aap apne logic ko define kar sakte hain watermark ko identify karne ke liye
                    # Example: Agar koi specific font ya transparency hai, usse remove karein
                    if "watermark" in s["text"].lower():
                        page.delete_textblock(b)
    doc.save(output_path)

# Bot ke zariye PDF file ko handle karna
def handle_pdf(update: Update, context):
    file = update.message.document.get_file()
    file.download("input.pdf")

    remove_watermark("input.pdf", "output.pdf")

    context.bot.send_document(chat_id=update.message.chat_id, document=open("output.pdf", "rb"))

# Telegram bot setup
def main():
    updater = Updater("5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_pdf))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
