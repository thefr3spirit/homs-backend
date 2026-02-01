# 🏨 Lemi Hotel Management System - Desktop App Integration Guide

**For: Gift (Desktop Counter App Developer)**  
**Date: January 31, 2026**

---

## 📋 Overview

Your desktop counter application needs to send daily hotel summary data to our backend API at the end of each business day. The backend will store this data in the cloud, making it available for the owner to view on their mobile app.

---

## 🌐 API Endpoint

### Base URL (Production - Live!)
```
https://homs-backend-txs8.onrender.com
```

### Testing the API
- Interactive docs: https://homs-backend-txs8.onrender.com/docs
- Alternative docs: https://homs-backend-txs8.onrender.com/redoc

---

## 📤 Sending Daily Summary

### Endpoint
```
POST /summary
```

### Full URL
```
https://homs-backend-txs8.onrender.com/summary
```

### Request Headers
```
Content-Type: application/json
```

### Request Body (JSON Format)
```json
{
  "date": "2026-01-31",
  "rooms_total": 20,
  "rooms_occupied": 8,
  "rooms_available": 12,
  "cash_collected": 350000.00,
  "momo_collected": 120000.00,
  "total_collected": 470000.00,
  "expected_balance": 470000.00,
  "expenses_logged": 20000.00
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | Yes | Date in YYYY-MM-DD format (e.g., "2026-01-31") |
| `rooms_total` | integer | Yes | Total number of rooms in the hotel |
| `rooms_occupied` | integer | Yes | Number of occupied rooms |
| `rooms_available` | integer | Yes | Number of available rooms |
| `cash_collected` | float | Yes | Amount collected in cash (local currency) |
| `momo_collected` | float | Yes | Amount collected via mobile money |
| `total_collected` | float | Yes | Total amount collected (cash + momo) |
| `expected_balance` | float | Yes | Expected balance for the day |
| `expenses_logged` | float | Yes | Total expenses logged for the day |

### ✅ Success Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2026-01-31",
  "rooms_total": 20,
  "rooms_occupied": 8,
  "rooms_available": 12,
  "cash_collected": 350000.0,
  "momo_collected": 120000.0,
  "total_collected": 470000.0,
  "expected_balance": 470000.0,
  "expenses_logged": 20000.0,
  "last_updated": "2026-01-31T18:30:45.123456"
}
```

### ❌ Error Responses

**400 Bad Request** - Invalid data format
```json
{
  "detail": [
    {
      "loc": ["body", "date"],
      "msg": "invalid date format",
      "type": "value_error"
    }
  ]
}
```

**500 Internal Server Error** - Server problem
```json
{
  "error": "Internal server error",
  "detail": "Failed to save summary"
}
```

---

## 💻 Code Examples

### Python Implementation
```python
import requests
import json
from datetime import date

def send_daily_summary(summary_data):
    """
    Send daily hotel summary to the backend API.
    
    Args:
        summary_data: Dictionary containing daily summary information
    
    Returns:
        Response object from the API
    """
    # API endpoint
    url = "http://192.168.X.X:8000/summary"  # Replace X.X with actual IP
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Send POST request
        response = requests.post(url, json=summary_data, headers=headers)
        
        # Check if successful
        if response.status_code == 201:
            print("✅ Summary sent successfully!")
            print("Response:", response.json())
            return response.json()
        else:
            print(f"❌ Error: {response.status_code}")
            print("Details:", response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Check network connection.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Prepare summary data
    summary = {
        "date": str(date.today()),  # Today's date
        "rooms_total": 20,
        "rooms_occupied": 8,
        "rooms_available": 12,
        "cash_collected": 350000.00,
        "momo_collected": 120000.00,
        "total_collected": 470000.00,
        "expected_balance": 470000.00,
        "expenses_logged": 20000.00
    }
    
    # Send to API
    send_daily_summary(summary)
```

### C# Implementation (.NET/WinForms/WPF)
```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class DailySummary
{
    [JsonProperty("date")]
    public string Date { get; set; }
    
    [JsonProperty("rooms_total")]
    public int RoomsTotal { get; set; }
    
    [JsonProperty("rooms_occupied")]
    public int RoomsOccupied { get; set; }
    
    [JsonProperty("rooms_available")]
    public int RoomsAvailable { get; set; }
    
    [JsonProperty("cash_collected")]
    public decimal CashCollected { get; set; }
    
    [JsonProperty("momo_collected")]
    public decimal MomoCollected { get; set; }
    
    [JsonProperty("total_collected")]
    public decimal TotalCollected { get; set; }
    
    [JsonProperty("expected_balance")]
    public decimal ExpectedBalance { get; set; }
    
    [JsonProperty("expenses_logged")]
    public decimal ExpensesLogged { get; set; }
}

public class ApiService
{
    private static readonly HttpClient client = new HttpClient();
    private const string BASE_URL = "http://192.168.X.X:8000"; // Replace X.X
    
    public static async Task<bool> SendDailySummary(DailySummary summary)
    {
        try
        {
            // Serialize to JSON
            string jsonContent = JsonConvert.SerializeObject(summary);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            
            // Send POST request
            HttpResponseMessage response = await client.PostAsync(
                $"{BASE_URL}/summary", 
                content
            );
            
            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("✅ Summary sent successfully!");
                string responseBody = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Response: {responseBody}");
                return true;
            }
            else
            {
                Console.WriteLine($"❌ Error: {response.StatusCode}");
                string errorBody = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Details: {errorBody}");
                return false;
            }
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"❌ Connection error: {ex.Message}");
            return false;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Unexpected error: {ex.Message}");
            return false;
        }
    }
}

// Example usage
class Program
{
    static async Task Main(string[] args)
    {
        var summary = new DailySummary
        {
            Date = DateTime.Today.ToString("yyyy-MM-dd"),
            RoomsTotal = 20,
            RoomsOccupied = 8,
            RoomsAvailable = 12,
            CashCollected = 350000.00m,
            MomoCollected = 120000.00m,
            TotalCollected = 470000.00m,
            ExpectedBalance = 470000.00m,
            ExpensesLogged = 20000.00m
        };
        
        await ApiService.SendDailySummary(summary);
    }
}
```

### JavaScript/Node.js Implementation
```javascript
const axios = require('axios');

const BASE_URL = 'http://192.168.X.X:8000'; // Replace X.X with actual IP

async function sendDailySummary(summaryData) {
    try {
        const response = await axios.post(
            `${BASE_URL}/summary`,
            summaryData,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
        
        console.log('✅ Summary sent successfully!');
        console.log('Response:', response.data);
        return response.data;
        
    } catch (error) {
        if (error.response) {
            console.error(`❌ Error: ${error.response.status}`);
            console.error('Details:', error.response.data);
        } else if (error.request) {
            console.error('❌ No response from server. Check network connection.');
        } else {
            console.error('❌ Unexpected error:', error.message);
        }
        return null;
    }
}

// Example usage
const summary = {
    date: new Date().toISOString().split('T')[0], // Today's date (YYYY-MM-DD)
    rooms_total: 20,
    rooms_occupied: 8,
    rooms_available: 12,
    cash_collected: 350000.00,
    momo_collected: 120000.00,
    total_collected: 470000.00,
    expected_balance: 470000.00,
    expenses_logged: 20000.00
};

sendDailySummary(summary);
```

---

## 🧪 Testing Your Integration

### 1. Test with Postman/Insomnia
Download Postman: https://www.postman.com/downloads/

**Steps:**
1. Open Postman
2. Create a new POST request
3. URL: `http://192.168.X.X:8000/summary`
4. Headers: `Content-Type: application/json`
5. Body → raw → JSON:
   ```json
   {
     "date": "2026-01-31",
     "rooms_total": 20,
     "rooms_occupied": 8,
     "rooms_available": 12,
     "cash_collected": 350000,
     "momo_collected": 120000,
     "total_collected": 470000,
     "expected_balance": 470000,
     "expenses_logged": 20000
   }
   ```
6. Click **Send**
7. You should see **201 Created** response

### 2. Test with cURL (Command Line)
```bash
curl -X POST "http://192.168.X.X:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-31",
    "rooms_total": 20,
    "rooms_occupied": 8,
    "rooms_available": 12,
    "cash_collected": 350000,
    "momo_collected": 120000,
    "total_collected": 470000,
    "expected_balance": 470000,
    "expenses_logged": 20000
  }'
```

### 3. View API Documentation
Open in browser: `http://192.168.X.X:8000/docs`

This interactive documentation lets you test all endpoints directly!

---

## 🔧 Implementation Checklist

- [ ] Install HTTP client library (requests, axios, HttpClient, etc.)
- [ ] Create data structure matching the JSON format
- [ ] Collect all required data from your desktop app
- [ ] Format date as YYYY-MM-DD
- [ ] Calculate `rooms_available = rooms_total - rooms_occupied`
- [ ] Calculate `total_collected = cash_collected + momo_collected`
- [ ] Send POST request to `/summary` endpoint
- [ ] Handle success response (201)
- [ ] Handle error responses (400, 500)
- [ ] Add retry logic if connection fails
- [ ] Log all transactions for debugging

---

## 📞 Connection Setup for Testing

### Getting the Backend IP Address

**Option 1: Same Local Network**
1. Backend team runs: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Look for IPv4 Address (e.g., 192.168.1.100)
3. Replace `192.168.X.X` with this IP in your code
4. Make sure both computers are on the same WiFi network

**Option 2: Remote Testing (Using ngrok)**
If you're not on the same network, backend team can use ngrok:
```bash
ngrok http 8000
```
This creates a public URL like: `https://abc123.ngrok.io`
Use this as your BASE_URL temporarily for testing.

**Option 3: Production Deployment (Coming Soon)**
Once deployed to cloud, you'll get a permanent URL like:
```
https://lemi-homs.onrender.com
```

---

## ⚠️ Important Notes

### Data Validation
- Date must be in **YYYY-MM-DD** format
- All numeric fields must be **non-negative**
- `rooms_available` should equal `rooms_total - rooms_occupied`
- `total_collected` should equal `cash_collected + momo_collected`

### When to Send
- Send summary **once per day** at end of business (e.g., 11:59 PM)
- If summary for date already exists, it will be **updated** (not duplicated)
- Store data locally first, then sync to cloud

### Error Handling
- If API is unreachable, store data locally
- Retry sending later (implement queue system)
- Log all failures for debugging
- Show user-friendly error messages

### Security (Production)
- Backend will be hosted on HTTPS (secure)
- May add API key authentication later
- Never hardcode credentials in your app

---

## 🆘 Troubleshooting

### "Connection refused" or "Cannot connect"
- ✅ Check if backend server is running
- ✅ Verify IP address is correct
- ✅ Ensure both devices are on same network
- ✅ Check firewall settings
- ✅ Ping the backend IP to test connectivity

### "400 Bad Request"
- ✅ Verify JSON format is correct
- ✅ Check all required fields are present
- ✅ Ensure date format is YYYY-MM-DD
- ✅ Verify numeric values are not strings

### "500 Internal Server Error"
- ✅ Contact backend team
- ✅ Check backend logs
- ✅ Database connection issue

---

## 📧 Support

**Backend Team Contact:**
- Developer: [Your Name]
- Email: [Your Email]
- Phone: [Your Phone]

**Questions? Issues?**
- Share error messages
- Provide request/response logs
- Test with Postman first to isolate issues

---

## 🎯 Quick Start Summary

1. **Get the backend IP address** from the team
2. **Choose your programming language** (Python/C#/JavaScript)
3. **Copy the code example** from this document
4. **Replace** `192.168.X.X` with actual IP
5. **Test** with sample data
6. **Integrate** into your desktop app
7. **Send daily summaries** automatically

---

**Good luck with the integration, Gift! 🚀**

*Last Updated: January 31, 2026*
