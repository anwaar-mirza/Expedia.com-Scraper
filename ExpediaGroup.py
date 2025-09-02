import csv
from playwright.sync_api import sync_playwright
from geopy.geocoders import ArcGIS
from threading import Thread
from Essential import GenericMethods
import pandas as pd
import time
import os


class ExpediaGroup(GenericMethods):
    def __init__(self):
        GenericMethods.__init__(self)
        self.arc = ArcGIS()

    def land_targeted_page(self, url):
        self.page.goto(url)
        time.sleep(2)

    def get_main_info(self, id, url):
        temp_amenities = {}
        title = self.get_element("//h1", timeout=600)
        try:
            address = self.page.locator('(//section[div//h2[contains(text(), "About the neighborhood")]])[2]//div[button]/div')
            address.wait_for(timeout=300)
            address.scroll_into_view_if_needed(timeout=1000)
            time.sleep(0.3)
            address = address.inner_text(timeout=300)
        except:
            address = ""
        if address != "":
            coor = self.arc.geocode(address)
            lat = coor.latitude
            lon = coor.longitude
        else:
            lat = ''
            lon = ''
        self.click_on_button("h1")
        time.sleep(1)
        self.click_on_button('button[aria-label="See all"]', timeout=1000)
        time.sleep(1)
        for val in self.amenities:
            required_selector = f'//div[div/h2[text()="{val}"]]//ul/li'
            results = self.get_elements(required_selector)
            temp_amenities[val.replace(" ", "_").lower()] = ', '.join(results)
        self.click_on_button('//button[@class="uitk-toolbar-button uitk-toolbar-button-icon-only"]')
        time.sleep(0.5)
        try:
            about_btn = self.page.locator('(//section[div/div//h2[contains(text(), "About this property")]])[2]//button')
            if not about_btn.is_visible():
                about_btn.scroll_into_view_if_needed(timeout=1000)
            about_btn.click(timeout=1000)
            time.sleep(1)
        except:
            pass
        about = self.get_element('(//section[div/div//h2[contains(text(), "About this property")]])[2]//div[@itemprop="description"]')
        image_btn = self.page.locator('//button[@class="uitk-button uitk-button-medium uitk-button-has-text uitk-button-overlay"]')
        if not image_btn.is_visible():
            image_btn.scroll_into_view_if_needed(timeout=1000)
        image_btn.click(timeout=1000, force=True)
        time.sleep(1)
        images = self.page.locator('//figure[@class="uitk-image uitk-image-ratio-16-9 uitk-image-ratio"]/div/img').all()
        for i in range(0, min(len(images), 300), 3):
            images[i].scroll_into_view_if_needed(timeout=3000)
        images = self.get_elements('//figure[@class="uitk-image uitk-image-ratio-16-9 uitk-image-ratio"]/div/img', attribute="src")
        self.click_on_button('//button[@class="uitk-toolbar-button uitk-toolbar-button-icon-only"]', timeout=1000)
        time.sleep(0.5)
        results = {
            "group_id": id,
            "user_id": "",
            "group_name": title,
            "group_desc": about,
            "post_image": ', '.join(images),
            "post_link": url
        }
        return results | temp_amenities | {"group_location": address, "lat": lat, "lon": lon}

    def get_policies(self, id):
        temp_policies = {}
        try:
            try:
                policy_btn = self.page.locator('(//section[div//h2[contains(text(), "Policies")]])[3]//button')
                policy_btn.wait_for(timeout=1000)
                if not policy_btn.is_visible():
                    policy_btn.scroll_into_view_if_needed(timeout=1000)
                policy_btn.click()
                time.sleep(1)
            except:
                pass
            for p in self.hotel_policies:
                required_xpath = f'//div[@data-stid="content-item" and div/div/h3[text()="{p}"]]//div[@class="uitk-layout-grid-item"]/div'
                temp_policies[p.replace(" ", "_").replace("-", "_").lower()] = ', '.join(self.get_elements(required_xpath))
            time.sleep(0.5)
            return {"id": "", "group_id": id} | temp_policies | {"created_at": ""}
        except:
            return {}
    
    def get_important_information(self, id):
        temp_extra = {}
        try:
            for val in self.extra_info:
                required_xpath = f'//div[@data-stid="content-item" and div/div/h3[text()="{val}"]]//div[@class="uitk-layout-grid-item"]/div'
                temp_extra[val.replace(" ", "_").replace("-", "_").lower()] = ', '.join(self.get_elements(required_xpath))
            return {"id": "", "group_id": id} | temp_extra | {"created_at": ""}
        except:
            return temp_extra
    
    def get_faqs(self, id):
        faqs = []
        try:
            check = self.page.locator('//h2[text() = "Frequently asked questions"]')
            check.wait_for(timeout=1000)
            if not check.is_visible():
                check.scroll_into_view_if_needed(timeout=1000)
            time.sleep(0.5)
            self.click_on_button('//button[@aria-label="Button to show more frequently asked questions"]', timeout=1000)
            time.sleep(0.5)
            questions = self.page.locator('//section//details[@class="uitk-expando uitk-expando-list-item"]//span//div').all()
            for q in questions:
                q.click(timeout=500)
                time.sleep(0.2)
            questions = self.get_elements('//section//details[@class="uitk-expando uitk-expando-list-item"]//span//div')
            answers = self.get_elements('//section//details[@class="uitk-expando uitk-expando-list-item"]/div/div/p')
            for q, a in zip(questions, answers):
                faqs.append({
                    "id": "",
                    "group_id": id,
                    "question": q,
                    "answer": a,
                    "created_at": ""
                })
            return faqs
        except:
            return faqs
    
    def get_beds(self, id):
        beds = []
        try:
            all_beds = self.page.locator('//div[@data-stid="section-room-list"]//span[text()= "More details"]').all()
            for bed in all_beds:
                temp_bed = {}
                bed.scroll_into_view_if_needed(timeout=500)
                bed.click(timeout=500)
                time.sleep(0.2)
                price_btn = self.page.locator('//div[@id="room-rates-options"]//button')
                price_btn.wait_for(timeout=1000)
                price_btn.scroll_into_view_if_needed(timeout=1000)
                time.sleep(0.2)
                bed_title = self.get_element('div[data-stid*="property-offers-details"] > h3')
                highlights = ', '.join(self.get_elements('//section[@aria-label="Room information"]//div[div/h3[text() = "Highlights"]]/div[2]/div'))
                # size = self.get_element('//section[@aria-label="Room information"]//ul//li[1]')
                # print(size)
                # bedroom_room = self.get_element('//section[@aria-label="Room information"]//ul//li[2]')
                # print(bedroom_room)
                # sleeps = self.get_element('//section[@aria-label="Room information"]//ul//li[3]')
                # print(sleeps)
                # queen_bed = self.get_element('//section[@aria-label="Room information"]//ul//li[4]')
                # print(queen_bed)
                temp_bed['id'] = ""
                temp_bed['group_id'] = id
                temp_bed['bed_title'] = bed_title
                temp_bed['highlights'] = highlights
                # temp_bed['size'] = size
                # temp_bed['bedroom_room'] = bedroom_room
                # temp_bed['sleeps'] = sleeps
                # temp_bed['queen_bed'] = queen_bed
                for val in self.room_features:
                    required_xpath = f'//div[@class="uitk-layout-grid-item" and div//h4[text() = "{val}"]]//ul/li'
                    temp_bed[val.replace(" ", "_").replace("-", "_").lower()] = ', '.join(self.get_elements(required_xpath))
                temp_bed['created_at'] = ""
                beds.append(temp_bed)
                self.click_on_button('//button[@class="uitk-toolbar-button uitk-toolbar-button-icon-only"]')
                time.sleep(0.2)

            return beds
        except Exception as e:
            print(e)
            return []


    def get_reviews(self, id):
        reviews = []
        try:
            revs = self.page.locator('(//section[div//h2[contains(text(), "Reviews")]])[2]//div[contains(@data-stid, "property-reviews")]').all()
            for r in revs:
                r.scroll_into_view_if_needed(timeout=500)
                time.sleep(0.2)
                try:
                    review_by = r.locator('xpath=.//h4').inner_text(timeout=500)
                except:
                    review_by = ''
                try:
                    review_date = r.locator('xpath=.//span[@itemprop="datePublished"]').inner_text(timeout=500)
                except:
                    review_date = ''
                try:
                    overall_rating = r.locator('xpath=.//span[@itemprop="ratingValue"]').inner_text(timeout=500)
                except:
                    overall_rating = '' 
                    
                try:
                    review_title = r.locator('xpath=.//h4[@data-stid="review_section_title"]/span').inner_text(timeout=500)
                except:
                    review_title = ''

                try:
                    review_body = r.locator('xpath=.//span[@itemprop="description"]').inner_text(timeout=500)
                except:
                    review_body = ''

                reviews.append(
                    {
                        "review_id": "",
                        "group_id": id,
                        "review_date": review_date,
                        "name": review_by,
                        "title": review_title,
                        "overall_rating": overall_rating,
                        "review": review_body,
                        "created_at": ""
                    }
                )
            return reviews
        except:
            return reviews

    def combine_all_sets(self, id, file_path, url):
        main = self.get_main_info(id, url)
        policies = self.get_policies(id)
        extra = self.get_important_information(id)
        faqs = self.get_faqs(id)
        beds = self.get_beds(id)
        reviews = self.get_reviews(id)

        main_df = pd.DataFrame([main])
        policies_df = pd.DataFrame([policies])
        extra_df = pd.DataFrame([extra])
        faqs_df = pd.DataFrame(faqs)
        beds_df = pd.DataFrame(beds)
        reviews_df = pd.DataFrame(reviews)

        sheet_map = {
            "users_portfolio_groups": main_df,
            "property_reviews": reviews_df,
            "property_beds": beds_df,
            "house_rules": policies_df,
            "faqs": faqs_df,
            "more_info": extra_df,
        }

        if os.path.exists(file_path):
            # File already exists → append without headers
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                for sheet, df in sheet_map.items():
                    if sheet in writer.sheets:
                        startrow = writer.sheets[sheet].max_row
                        df.to_excel(
                            writer,
                            sheet_name=sheet,
                            index=False,
                            header=False,
                            startrow=startrow,
                        )
                    else:
                        # If a new sheet is added later → include headers
                        df.to_excel(writer, sheet_name=sheet, index=False)
        else:
            # First time → write with headers
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                for sheet, df in sheet_map.items():
                    df.to_excel(writer, sheet_name=sheet, index=False)



def handle_threading(thread_id, group_id, url_file_path, output_file_path):
    bot = ExpediaGroup()
    if os.path.exists(url_file_path):
        with open(url_file_path, 'r') as f:
            next(f)
            reading_file = csv.reader(f)
            i=0
            for id, url in enumerate(reading_file, start=group_id):
                i+=1
                print(f"Thread {thread_id}: Processing ID: {id}, Current Link: {i}, URL: {url[0]}")
                bot.land_targeted_page(url=url[0].strip())
                bot.combine_all_sets(id=id, file_path=output_file_path, url=url[0].strip())


th1 = Thread(target=handle_threading, args=(1, 424, r"C:\Users\anwaa\Downloads\1_100.csv", 'D:/ExpediaGroup_1.xlsx'))
th1.start()
th2 = Thread(target=handle_threading, args=(2, 524, r"C:\Users\anwaa\Downloads\100_200_links.csv", 'D:/ExpediaGroup_2.xlsx'))
th2.start()
th3 = Thread(target=handle_threading, args=(3, 624,r"C:\Users\anwaa\Downloads\200_300 (1).csv" , 'D:/ExpediaGroup_3.xlsx'))
th3.start()


th1.join()
th2.join()
th3.join()
