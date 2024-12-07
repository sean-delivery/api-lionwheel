"""
                    },
                    {"role": "user", "content": conversation}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"שגיאה בעיבוד השיחה: {str(e)}")
            return None

    def validate_phone_number(self, phone):
        """
        בדיקת תקינות מספר טלפון
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "בדוק אם מספר הטלפון תקין (מתחיל ב-05 או 07 ומכיל 10 ספרות). החזר true או false."
                    },
                    {"role": "user", "content": phone}
                ]
            )
            return response.choices[0].message.content.lower() == "true"
        except Exception as e:
            print(f"שגיאה בבדיקת מספר טלפון: {str(e)}")
            return False

    def validate_address(self, city, street, number):
        """
        בדיקת תקינות כתובת
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "בדוק אם הכתובת תקינה (עיר קיימת בישראל, שם רחוב הגיוני ומספר בית חוקי). החזר true או false."
                    },
                    {"role": "user", "content": f"{city}, {street} {number}"}
                ]
            )
            return response.choices[0].message.content.lower() == "true"
        except Exception as e:
            print(f"שגיאה בבדיקת כתובת: {str(e)}")
            return False

    def create_lionwheel_json(self, delivery_info):
        """
        יוצר JSON בפורמט המתאים ל-Lionwheel
        """
        return {
            "pickup_at": delivery_info.get("pickup_date"),
            "company_id": self.company_id,
            "הערות": delivery_info.get("pickup_notes", ""),
            "original_order_id": f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source_city": delivery_info.get("pickup_city"),
            "source_street": delivery_info.get("pickup_street"),
            "source_number": delivery_info.get("pickup_building_number"),
            "source_phone": delivery_info.get("pickup_phone"),
            "destination_city": delivery_info.get("delivery_city"),
            "destination_street": delivery_info.get("delivery_street"),
            "destination_number": delivery_info.get("delivery_building_number"),
            "destination_notes": delivery_info.get("delivery_notes", ""),
            "destination_phone": delivery_info.get("delivery_phone"),
            "delivery_method": "רכב",
            "packages_quantity": 1,
            "money_collect": 0,
            "is_tour": False,
            "is_self_pickup": False,
            "earliest": delivery_info.get("pickup_time"),
            "latest": delivery_info.get("delivery_time"),
            "line_items": [],
            "דחיפות": 0
        }

    def create_delivery(self, delivery_info):
        """
        יוצר משלוח חדש במערכת Lionwheel
        """
        try:
            # בדיקת תקינות הנתונים
            if not self.validate_phone_number(delivery_info.get("pickup_phone")) or \
               not self.validate_phone_number(delivery_info.get("delivery_phone")):
                raise ValueError("מספר טלפון לא תקין")

            if not self.validate_address(
                delivery_info.get("pickup_city"),
                delivery_info.get("pickup_street"),
                delivery_info.get("pickup_building_number")
            ) or not self.validate_address(
                delivery_info.get("delivery_city"),
                delivery_info.get("delivery_street"),
                delivery_info.get("delivery_building_number")
            ):
                raise ValueError("כתובת לא תקינה")

            json_data = self.create_lionwheel_json(delivery_info)
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"שגיאה ביצירת המשלוח: {str(e)}")
            return None
        except ValueError as e:
            print(f"שגיאה בנתונים: {str(e)}")
            return None

    def update_crm(self, delivery_info, delivery_response):
        """
        מעדכן את מערכת ה-CRM עם פרטי המשלוח
        """
        crm_json = {
            "pickup_city": delivery_info.get("pickup_city"),
            "pickup_street": delivery_info.get("pickup_street"),
            "pickup_building_number": delivery_info.get("pickup_building_number"),
            "pickup_notes": delivery_info.get("pickup_notes"),
            "pickup_phone": delivery_info.get("pickup_phone"),
            "delivery_city": delivery_info.get("delivery_city"),
            "delivery_street": delivery_info.get("delivery_street"),
            "delivery_building_number": delivery_info.get("delivery_building_number"),
            "delivery_notes": delivery_info.get("delivery_notes"),
            "delivery_phone": delivery_info.get("delivery_phone"),
            "pickup_date": delivery_info.get("pickup_date"),
            "pickup_time": delivery_info.get("pickup_time"),
            "delivery_date": delivery_info.get("delivery_date"),
            "delivery_time": delivery_info.get("delivery_time"),
            "lionwheel_order_id": delivery_response.get("order_id", "")
        }
        return crm_json

def main():
    # יצירת מופע של המערכת
    delivery_system = LionwheelDeliverySystem()
