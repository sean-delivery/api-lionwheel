
```python
import requests
import json
from datetime import datetime
from openai import OpenAI

class LionwheelDeliverySystem:
    def __init__(self):
        self.openai_client = OpenAI(api_key="olfao2CYx0I7nF1CGs917GyefdEoyV5pib1rg6JX078zUSMuRveETrDaDzygPGkl6_UG9e59j8T3BlbkFJGykLBZh2mZeBozXJxcO9yjJ8cIyaNJGOGz4VJbDdq69Rso1p2uTWIqRywbbUJ9BGStD3o29esA")
        self.api_url = "https://members.lionwheel.com/api/v1/tasks/create"
        self.api_key = "3349359b-87f4-483d-a114-75a8776917f4"
        self.company_id = 51068
        self.headers = {
            'Content-Type': 'application/json'
        }
        
    def collect_delivery_info(self, conversation):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        אתה עוזר משלוחים של חברת שון. תפקידך לנתח שיחות עם לקוחות ולהחזיר JSON מסודר.
                        
                        כללים חשובים:
                        1. חלץ רק מידע שקיים בשיחה
                        2. אל תמציא נתונים
                        3. החזר JSON בפורמט הבא בדיוק:
                        {
                            "pickup_city": "עיר איסוף",
                            "pickup_street": "רחוב איסוף",
                            "pickup_building_number": "מספר בניין איסוף",
                            "pickup_notes": "הערות לאיסוף",
                            "pickup_phone": "טלפון איסוף",
                            "delivery_city": "עיר מסירה",
                            "delivery_street": "רחוב מסירה",
                            "delivery_building_number": "מספר בניין מסירה",
                            "delivery_notes": "הערות למסירה",
                            "delivery_phone": "טלפון מסירה",
                            "pickup_date": "תאריך איסוף",
                            "pickup_time": "שעת איסוף",
                            "delivery_date": "תאריך מסירה",
                            "delivery_time": "שעת מסירה"
                        }
                        
                        שים לב:
                        - אל תשנה את שמות השדות באנגלית
                        - אם חסר מידע, השאר את השדה ריק
                        - החזר רק את ה-JSON, בלי טקסט נוסף
                        """
                    },
                    {"role": "user", "content": conversation}
                ],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"שגיאה בעיבוד השיחה: {str(e)}")
            return None

    def create_delivery(self, delivery_info):
        try:
            json_data = {
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
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"שגיאה ביצירת המשלוח: {str(e)}")
            return None

def main():
    # יצירת מופע של המערכת
    delivery_system = LionwheelDeliverySystem()
    
    # דוגמה לשיחה עם לקוח
    conversation = """
    אני צריך לשלוח חבילה מתל אביב לירושלים.
    כתובת האיסוף: דיזנגוף 123, תל אביב, קומה 3 דירה 5
    טלפון לאיסוף: 0541234567
    כתובת המסירה: יפו 456, ירושלים, קומה 1 דירה 2
    טלפון למסירה: 0529876543
    זמן איסוף: מחר ב-10:00
    זמן מסירה רצוי: מחר ב-14:00
    """
    
    # איסוף מידע מהשיחה
    delivery_info = delivery_system.collect_delivery_info(conversation)
    if delivery_info:
        # יצירת המשלוח
        delivery_response = delivery_system.create_delivery(json.loads(delivery_info))
        if delivery_response:
            print("המשלוח נוצר בהצלחה!")
            print(f"מספר הזמנה: {delivery_response.get('order_id', '')}")
        else:
            print("שגיאה ביצירת המשלוח")
    else:
        print("שגיאה באיסוף המידע מהשיחה")

if __name__ == "__main__":
    main()
```
