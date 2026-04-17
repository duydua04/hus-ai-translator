import time
import random
import logging
from typing import List, Dict, Set, Tuple
from DrissionPage import ChromiumPage, ChromiumOptions

logger = logging.getLogger(__name__)


class ReadToLeadScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def _get_chrome_options(self) -> ChromiumOptions:
        """Tao port ngau nhien de crawl song song"""
        co = ChromiumOptions()
        co.set_local_port(random.randint(9200, 9999))

        co.set_browser_path('/usr/bin/chromium')

        if self.headless:
            co.headless()

        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--mute-audio')
        return co

    def get_total_pages(self, base_url: str) -> int:
        """
        Mở trang chủ, cuộn xuống cuối, tìm thanh phân trang và trả về tổng số trang lớn nhất.
        """
        page = ChromiumPage(self._get_chrome_options())
        max_page = 1

        try:
            logger.info(f"Đang trinh sát tổng số trang tại: {base_url}")
            page.get(base_url)

            page.wait.doc_loaded(timeout=10)

            logger.info("Đang cuộn xuống đáy trang...")
            page.scroll.to_bottom()
            time.sleep(3)

            last_page_ele = page.ele('css:.page-nav a.last')

            if last_page_ele:
                max_page = int(last_page_ele.text.replace(',', '').replace('.', '').strip())
                logger.info(f"Dã tìm thấy tổng cộng {max_page} trang (qua thẻ .last)!")

            else:
                page_elements = page.eles('css:.page-nav a.page')
                nums = []
                for p in page_elements:
                    txt = p.text.replace(',', '').replace('.', '').strip()
                    if txt.isdigit():
                        nums.append(int(txt))

                if nums:
                    max_page = max(nums)
                    logger.info(f"Đã tìm thấy tổng cộng {max_page} trang (qua mảng .page)!")
                else:
                    logger.warning("Không tìm thấy phân trang, mặc định cào 1 trang.")

        except Exception as e:
            logger.error(f"Lỗi khi tìm số trang: {e}")
        finally:
            page.quit()

        return max_page

    def scrape_page(self, p_num: int, base_url: str, processed_links: Set[str]) -> Tuple[int, List[Dict]]:
        """
        Xu ly trang va tra ve du lieu cao duoc.
        """
        page = ChromiumPage(self._get_chrome_options())
        data_of_page = []

        try:
            list_url = f"{base_url}/page/{p_num}/" if p_num > 1 else base_url
            logger.info(f"[Page {p_num}] scanning")
            page.get(list_url)

            elements = page.eles('css:.tdb_module_loop_2 .entry-title a')
            all_links = [a.link.rstrip('/') for a in elements]

            processed_normalized = {p.rstrip('/') for p in processed_links}
            new_links = list(
                dict.fromkeys([l for l in all_links if l not in processed_normalized])
            )

            logger.info(f"[Page {p_num}] Tổng: {len(all_links)} bài | Cần cào mới: {len(new_links)} bài")

            for link in new_links:
                article_data = self._scrape_single_article(page, link)
                data_of_page.extend(article_data)

        except Exception as e:
            logger.error(f"[Page {p_num}] Lỗi quét trang: {e}")
        finally:
            page.quit()

        return p_num, data_of_page

    def _scrape_single_article(self, page: ChromiumPage, link: str, retries: int = 3) -> List[Dict]:
        """Logic bóc tách chi tiết song ngữ (Đã bọc cơ chế Retry chống lỗi Refresh)"""
        current_article_data = []

        for attempt in range(1, retries + 1):
            try:
                page.get(link)
                page.wait.doc_loaded(timeout=10)
                page.run_js(
                    "document.querySelectorAll('a.bg-showmore-plg-link').forEach(btn => { if(btn.innerText.includes('Hiển thị')) btn.click(); });"
                )

                time.sleep(1.5)

                blocks = page.eles('.bg-margin-for-link')
                for block in blocks:
                    vi_div = block.ele('css:div[id^="bg-showmore-hidden"]')
                    vi_text = vi_div.text if vi_div else ""

                    en_text = ""
                    prev_node = block.prev()
                    while prev_node:
                        p_text = prev_node.text.strip()
                        if len(p_text) > 10 and "tiếng Việt" not in p_text:
                            en_text = p_text
                            break
                        prev_node = prev_node.prev()

                    if en_text and vi_text:
                        current_article_data.append({
                            'English': en_text,
                            'Vietnamese': vi_text,
                        })

                return current_article_data

            except Exception as e:
                error_msg = str(e)
                if "The page is refreshed" in error_msg or "disconnected" in error_msg:
                    if attempt < retries:
                        logger.warning(f"[Retry {attempt}/{retries}] Web giật lag tại {link}. Đang tải lại...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error(f"Bỏ cuộc sau {retries} lần thử tại bài {link}: {e}")
                else:
                    logger.error(f"Lỗi bài {link}: {e}")
                    break

        return current_article_data