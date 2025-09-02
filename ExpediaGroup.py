from playwright.sync_api import sync_playwright
from geopy.geocoders import ArcGIS
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
        # address = self.get_element('//div[@data-stid="content-hotel-address"]', timeout=600)
        # if address != "":
        #     coor = self.arc.geocode(address)
        #     lat = coor.latitude
        #     lon = coor.longitude
        # else:
        #     lat = ''
        #     lon = ''
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
        return results | temp_amenities 
    # | {"address": address, "lat": lat, "lon": lon}

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
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                for sheet, df in sheet_map.items():
                    if sheet in writer.sheets:
                        startrow = writer.sheets[sheet].max_row
                        df.to_excel(writer, sheet_name=sheet, index=False, header=False, startrow=startrow)
                    else:
                        # if new sheet is added later → create with headers
                        df.to_excel(writer, sheet_name=sheet, index=False)
        else:
            # create new file → headers included
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                for sheet, df in sheet_map.items():
                    df.to_excel(writer, sheet_name=sheet, index=False)

urls_list = [
    # "https://www.expedia.com/Harare-Hotels-Sharon-Las-Palmas-Guest-House.h95375990.Hotel-Information?",
    # "https://www.expedia.com/Bouvet-Island-Hotels-Vrbo-Property.h48288270.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Cheltenham-Park-Resort.h101320617.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-The-Peech-Boutique-Hotel.h100845560.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Marcifen.h115148261.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Cottage-In-Harare-Near-Westgate.h111835722.Hotel-Information?",
    # "https://www.expedia.com/Dakeni-Game-Farm.h114408699.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Silver-Moon-Guest-House.h112412703.Hotel-Information?",
    # "https://www.expedia.com/Bulawayo-Hotels-Gwango-Tamarillo-Estate.h113584537.Hotel-Information?",
    # "https://www.expedia.com/Bouvet-Island-Hotels-Charming-One-Bedroom-Apartment.h109821359.Hotel-Information?",
    # "https://www.expedia.com/Juliasdale-Hotels-Rupurara-Valley-Lodge.h109574152.Hotel-Information?",
    # "https://www.expedia.com/Chinhoyi-Hotels-Welcome-To-The-Zebra-Room.h82989578.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-The-Victoria-Falls-Hotel.h24943.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Kafusi-Lodge.h101433636.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Shearwater-Explorers-Village.h18030489.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Kasambabezi-Lodge.h116783828.Hotel-Information?",
    # "https://www.expedia.com/Gweru-Hotels-Quaint-Cabin-With-WiFi-In-Charming-Gweru.h117832256.Hotel-Information?",
    # "https://www.expedia.com/Goromonzi-Hotels-Pachigomo-Guest-House.h40052203.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-The-Telescope-Boutique-Lodge.h114264914.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Cozy-And-Stylish-Room.h108985235.Hotel-Information?",
    # "https://www.expedia.com/Matopos-Hotels-Matobo-Hills-Lodge.h2150542.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Malcolm-Lodge.h15475962.Hotel-Information?",
    # "https://www.expedia.com/Bulawayo-Hotels-Neat-One-Bedroom-In-Morningside-Guesthouse-2091.h94944869.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Family-Friendly-Environment-With-A-Big-Garden-And-Barbeque-Area.h111135410.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-The-Manor-House.h116523247.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-The-Courtney-Lodge.h93663273.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-258-Hotel.h110380298.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Phezulu-Lodge.h23665555.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Shailoh-Folyjon-2Bedroomed-Wing.h33056835.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Wild-Trekkers-Lodge.h10636191.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-1-Bed-Apartment-In-Mount-Pleasant-Heights-2014.h89962429.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-2-Bed-Apartment-With-En-Suite-Kitchenette-2064.h94945673.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Marts-Place-Full-Solar-Power-Wi-Fi.h95698581.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Vrbo-Property.h41656253.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Residence-Hotel.h93528792.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-528-Victoria-Falls-Guest-House.h36026343.Hotel-Information?",
    # "https://www.expedia.com/Mutare-Hotels-2-Bedroomed-House-With-A-Lovely-Garden-2177.h100192417.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Amakhosi-Hotel.h112603051.Hotel-Information?",
    # "https://www.expedia.com/Kariba-Hotels-Warthogs-Safari-Camp.h23986992.Hotel-Information?",
    # "https://www.expedia.com/Zvishavane-Hotels-Enchanted-Africa-Apartments.h113578341.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Togara-Guest-House.h41653260.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-2-Bedroomed-Apartment-With-En-Suite-And-Kitchenette-2066.h94943394.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Lulu-Guest-Lodge.h96840734.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Elephant-Hills-Resort.h536395.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Vrbo-Property.h41656251.Hotel-Information?",
    # "https://www.expedia.com/Bulawayo-Hotels-UPhondo-Lodge.h114141769.Hotel-Information?",
    # "https://www.expedia.com/Kadoma-Hotels-PaLuana-Lodges-Kadoma.h115990705.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Mt-Pleasant-Bed-And-Breakfast.h110719126.Hotel-Information?",
    # "https://www.expedia.com/Masvingo-Hotels-Luxury-3-Bedroom-Self-Catering-Apartment-Masvingo.h103075359.Hotel-Information?",
    # "https://www.expedia.com/Hurungwe-Hotels-Spring-Resort.h99931398.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-The-Hayhill-Treetop-Escape-Apartment-Offers-Scenic-Views-Overlooking-Harare.h119450942.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-The-Best-Green-Garden-Guest-House-In-Harare.h75432989.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Liam-Villas-Newlands.h115156772.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Cresta-Jameson.h6220.Hotel-Information?",
    # "https://www.expedia.com/Beatrice-Hotels-Beatrice-Lodges-And-Conference-Centre.h30055311.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Liam-Victoria-Falls.h95240288.Hotel-Information?",
    # "https://www.expedia.com/1-Bed-Apartment-In-Mount-Pleasant-Heights-2013.h94944758.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Stephen-Margolis-Resort.h27364660.Hotel-Information?",
    # "https://www.expedia.com/Bulawayo-Hotels-Cozy-2-Bed-2-Bath-Apartment.h102313129.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Grosvenor-House.h88324018.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-Amazing-Apartment-With-WiFi-In-Vibrant-Harare.h115094057.Hotel-Information?",
    # "https://www.expedia.com/Bulawayo-Hotels-Motsamai-Lodge.h12696840.Hotel-Information?",
    # "https://www.expedia.com/Harare-Hotels-2-Bed-Roomed-Fully-Furnished-And-Secure-Apartment.h37207486.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Drift-Inn.h91341587.Hotel-Information?",
    # "https://www.expedia.com/Victoria-Falls-Hotels-Dumisa-African-Home.h48392669.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Bhejane-Lodge.h92330586.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-Holiday-Inn-Bulawayo.h49292.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-Neat-Standard-Room-In-Guesthouse-2088.h94944238.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Private-And-Charming-Room-In-Avondale.h106043272.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Miombo-Mews.h93413186.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Cresta-Lodge-Harare.h18938322.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Highlands-Lodges-And-Apartments.h21955172.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Solar-Powered-3-Bed-Haven-In-Bannatyne-Park.h109935467.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-The-Hilltop-Guesthouse.h103834870.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Casa-Favorita.h108701295.Hotel-Information?",
    "https://www.expedia.com/Mount-Hampden-Hotels-CARTM-Apartments.h115695768.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-1-Bed-Apartment-In-Mount-Pleasant-Heights-2013.h89962431.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-N1-Hotel-Samora-Machel-Harare.h10478758.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-The-Country-Club.h113949543.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-3-Bedroom-House-In-Charming-Bulawayo-With-WiFi.h115969997.Hotel-Information?",
    "https://www.expedia.com/Mutare-Hotels-Madrugada-Magic.h23192238.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Luxurious-2-Bedroom-Apartment-In-Harare-North.h116317042.Hotel-Information?",
    "https://www.expedia.com/Gweru-Hotels-3-Bed-Cozy-Homestay-For-Groups-In-Lundi-Park-2292.h115384875.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Bhejane-Lodge.h92330586.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Victoria-Falls-Rainbow-Hotel.h2150531.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-Breeze-Guest-House.h24282938.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Fidelity-Lodgings-And-Travel.h107066976.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Shongwe-Lookout.h34280264.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Starz-Place-In-The-Avenues.h118078703.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Bethel-Lodgings.h103422690.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-2-Bed-Apartment-With-Ensuite-Kitchenette-2071.h94943739.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-2-Bed-Guesthouse-In-Mabelreign-2012.h94943736.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-The-N1-Hotel-Bulawayo.h10483770.Hotel-Information?",
    "https://www.expedia.com/Kotwa-Hotels-The-Pumpkin-Hotel.h6609995.Hotel-Information?",
    "https://www.expedia.com/Bulawayo-Hotels-Musketeers-Lodge.h5494473.Hotel-Information?",
    "https://www.expedia.com/Victoria-Falls-Hotels-Victoria-Falls-Oasis-Hotel.h117821672.Hotel-Information?",
    "https://www.expedia.com/Macheke-Lodges-Conference-Centre.h45162241.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Pemabwe.h93416448.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Cosy-2-Bedroom-Retreat-With-Garden.h115856072.Hotel-Information?",
    "https://www.expedia.com/Dete-Hotels-Hwange-Safari-Lodge.h1159499.Hotel-Information?",
    "https://www.expedia.com/Harare-Hotels-Graceland-Guesthouse.h40913090.Hotel-Information?"

]

group_id = int(input("Enter Group ID starting number: "))
file_path = input("Enter file path with file name and extension (e.g., D:/ScrapingProjects/ExpediaGroup/output.xlsx): ")
bot = ExpediaGroup()
for id, url in enumerate(urls_list, start=group_id):
    bot.land_targeted_page(url)
    bot.combine_all_sets(id=id, file_path=file_path, url=url)
