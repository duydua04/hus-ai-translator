from DrissionPage import ChromiumPage, ChromiumOptions
import pandas as pd
import time
import os
from utils.bucket_manager import BucketManager
from datetime import datetime
class CrawlData:
    def __init__(self):
        """
        Khởi tạo cấu hình và kết nối cần thiết cho việc crawl dữ liệu.
        """
        self.base_url = "https://readtoolead.com"
        self.manager = BucketManager()
        co = ChromiumOptions()
        
        # 1. Chế độ ẩn (BẮT BUỘC TRÊN DOCKER)
        co.headless(True) 
        
        # 2. Vượt rào lỗi bảo mật SSL (Hoa đã test thành công trên máy thật)
        co.set_argument('--ignore-certificate-errors')
        co.set_argument('--ignore-ssl-errors')
        
        # 3. Cấu hình "Sống Còn" cho Docker Linux
        co.set_argument('--no-sandbox')            # Vượt rào bảo mật root
        co.set_argument('--disable-dev-shm-usage') # Dùng RAM hệ thống (tránh crash do thiếu bộ nhớ đệm)
        co.set_argument('--disable-gpu')           # Docker không có card đồ họa
        
        # 4. Giả lập trình duyệt thật (Để web không chặn Bot)
        co.set_argument('--lang=en-US')
        co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # 5. Đường dẫn đến Chromium
        co.set_browser_path('/usr/bin/chromium') 
        
        # 6. Tránh lỗi quyền ghi file (Quyết định việc 'Disconnected' hay không)
        co.set_user_data_path('/tmp/drission_user_data')

        self.co = co
        self.page = ChromiumPage(self.co)


    def get_article_links(self, page_num):
        """
        Lấy tất cả link bài viết trên trang danh sách.
        """
        links = []
        try:
            list_url = f"{self.base_url}/page/{page_num}/" if page_num > 1 else self.base_url
            print(f"\n--- Đang quét trang {page_num} ---")

            self.page.get(list_url)

            all_elements = self.page.eles('css:.tdb_module_loop_2 .entry-title a')

            all_links = [a.link for a in all_elements]
            print(f"Tìm thấy : {len(all_links)} bài báo")
            return list(set(all_links)) # Xóa link trùng và trả về luôn
        
            
        except Exception as e:
            print(f"Lỗi lấy link trang {page_num}: {e}")
            return []



    def _extract_article_detail(self, url):
        """
        Lấy chi tiết bài viết: Title, Post Date, và các cặp EN-VI.
        """
        try:
            self.page.get(url)
            print(f" Đang xử lý bài: {url}")
           # JS Click đồng loạt
            self.page.run_js("document.querySelectorAll('a.bg-showmore-plg-link').forEach(btn => { if(btn.innerText.includes('Hiển thị Tiếng Việt')) btn.click(); });")
            time.sleep(1.2)
            
            title = self.page.ele('tag:h1').text if self.page.ele('tag:h1') else "No Title"
            post_date = self.page.ele('css:time.entry-date').attr('datetime') if self.page.ele('css:time.entry-date') else "No Date"
            blocks = self.page.eles('.bg-margin-for-link')

            current_article_data = []
            for block in blocks:
                vi_div = block.ele('css:div[id^="bg-showmore-hidden"]')
                vi_text = vi_div.text if vi_div else ""
                
                # Duyệt ngược vét cạn tìm English
                en_text = ""
                prev_node = block.prev()
                while prev_node:
                    p_text = prev_node.text.strip()
                    junk_keywords = ["Source:", "WORD BANK:", "Read more:"]
                    if len(p_text) > 10 and not any(keyword in p_text for keyword in junk_keywords):
                        en_text = p_text
                        break
                    prev_node = prev_node.prev()
                
                if en_text and vi_text:
                    if "WORD BANK" not in vi_text and "Source:" not in vi_text:
                        current_article_data.append({
                            'Article_Title': title,
                            'Post_Date': post_date,
                            'English': en_text,
                            'Vietnamese': vi_text,
                            'url': url
                        })
            print(f" Đã trích xuất {len(current_article_data)} cặp EN-VI từ bài này.")
            return current_article_data
        
        except Exception as e:
            print(f"Lỗi lấy chi tiết bài {url}: {e}")
            return []   


    def crawl_and_save(self, start_page, end_page):
        """
        Quản lý toàn bộ quá trình crawl từ start_page đến end_page, gom dữ liệu, và lưu lên MinIO.
        """
        all_articles_data = []
        for p_num in range(start_page, end_page + 1):
            print(f" Bắt đầu xử lý Trang {p_num}...")
            links = self.get_article_links(p_num)
            if not links:
                print(f"Trang {p_num} không có bài nào hoặc bị lỗi.")
                continue
            
            for link in links:
                article_data = self._extract_article_detail(link) # Trả về List các Dict
                if article_data:
                    # Gom dữ liệu bài này vào thùng chứa chung
                    all_articles_data.extend(article_data) 
                    print(f" Đã bóc tách xong: {link}")
            
            time.sleep(1)
    
        if all_articles_data:
            # Biến tất cả thành 1 DataFrame duy nhất
            df_final = pd.DataFrame(all_articles_data)
            
            # Đặt tên file theo khoảng trang cho rõ ràng
            file_name = f"readtolead_pages_{start_page}_to_{end_page}"
            
            # Lưu 1 file duy nhất lên MinIO
            self.manager.save_dataframe(
                df=df_final,
                bucket='readtolead-lake',
                folder='raw',
                file_name=file_name,
                file_format='json'
            )
            print(f"\n HOÀN THÀNH! Đã gom {len(all_articles_data)} đoạn văn vào file: {file_name}")
        else:
            print(" Không có dữ liệu nào để lưu.")


# --- CHẠY CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    crawler = CrawlData()
    crawler.crawl_and_save(start_page=1, end_page=10)