/**
 * Vercel Serverless Function - SMS Proxy for SerwerSMS.pl
 * YO&GO Events SMS Sender
 * 
 * Deploy na Vercel - będzie dostępne pod adresem:
 * https://twoja-nazwa.vercel.app/api
 */

export default async function handler(req, res) {
    // CORS headers - pozwalają na wywołania z przeglądarki
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    // Obsługa preflight request (OPTIONS)
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // Sprawdź czy to POST request
    if (req.method !== 'POST') {
        res.status(405).json({ 
            success: false, 
            error: 'Metoda musi być POST' 
        });
        return;
    }

    try {
        const { username, password, action = 'send', phone, text, sender = 'YOGOEvents' } = req.body;

        // Sprawdź wymagane dane
        if (!username || !password) {
            res.status(400).json({ 
                success: false, 
                error: 'Brak loginu lub hasła' 
            });
            return;
        }

        let apiUrl, postData;

        if (action === 'test') {
            // Test połączenia - sprawdź limit/saldo
            apiUrl = 'https://api.serwersms.pl/v1/messages/limit';
            postData = new URLSearchParams({
                username: username,
                password: password,
                format: 'json'
            });
        } else {
            // Wysyłanie SMS
            if (!phone || !text) {
                res.status(400).json({ 
                    success: false, 
                    error: 'Brak numeru telefonu lub treści wiadomości' 
                });
                return;
            }

            apiUrl = 'https://api.serwersms.pl/v1/messages/send_sms';
            postData = new URLSearchParams({
                username: username,
                password: password,
                phone: phone,
                text: text,
                sender: sender,
                format: 'json'
            });
        }

        // Wykonaj request do SerwerSMS
        console.log(`${new Date().toISOString()} - ${action} request for user: ${username}`);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'YOGOEvents-SMS-Sender/1.0'
            },
            body: postData.toString()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        
        // Zwróć wynik
        res.status(200).json(result);

    } catch (error) {
        console.error('Error processing request:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message || 'Błąd serwera proxy' 
        });
    }
}