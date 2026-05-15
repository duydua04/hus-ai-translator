from pipeline import DocumentTranslationPipeline

# Dịch PDF từ tiếng Anh sang tiếng Việt
pipeline = DocumentTranslationPipeline(
    service="google",  # Free, không cần API key
    lang_in="en",
    lang_out="vi"
)

print("Bắt đầu dịch PDF...")
result = pipeline.translate(
    input_pdf="UCSC.pdf",
    output_pdf="UCSC_output_vi.pdf",
    verbose=True
)

if result["status"] == "success":
    print("\nDịch thành công!")
    print(f"File output: {result['output_pdf']}")
    print(f"Thời gian: {result['duration_seconds']:.1f}s")
    print(f"Số trang: {result['stats']['page_count']}")
else:
    print(f"\nLỗi: {result['error']}")