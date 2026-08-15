from flask import Flask, request, jsonify
from textblob import TextBlob
import random
import time
import os

app = Flask(__name__)

# Configuration
MODEL_PORT = int(os.getenv('MODEL_PORT', 5000))

# Global state for admin simulation
model_healthy = True

def analyze_sentiment_and_rating(text):
    """
    Analyze sentiment and generate pseudo rating based on sentiment
    """
    try:
        # Use TextBlob for sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Range: -1 (negative) to 1 (positive)
        
        # Determine sentiment category
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Determine confidence level
        abs_polarity = abs(polarity)
        if abs_polarity > 0.5:
            confidence = "high"
        elif abs_polarity > 0.2:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate pseudo rating based on sentiment (1-5 stars)
        if sentiment == "positive":
            # Positive: 4-5 stars, higher polarity = higher rating
            base_rating = 4.0 + (polarity * 1.0)  # 4.0 to 5.0
            rating = round(min(5.0, max(4.0, base_rating)), 1)
        elif sentiment == "negative":
            # Negative: 1-2 stars, more negative = lower rating
            base_rating = 2.0 + (polarity * 1.0)  # 1.0 to 2.0 (since polarity is negative)
            rating = round(max(1.0, min(2.0, base_rating)), 1)
        else:
            # Neutral: around 3 stars with slight variation
            base_rating = 3.0 + (polarity * 0.5)  # 2.5 to 3.5
            rating = round(max(2.5, min(3.5, base_rating)), 1)
        
        return {
            "sentiment": sentiment,
            "score": round(polarity, 3),
            "confidence": confidence,
            "rating": rating
        }
    
    except Exception as e:
        # Fallback to neutral if analysis fails
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "confidence": "low",
            "rating": 3.0,
            "error": str(e)
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes and backend monitoring"""
    
    if not model_healthy:
        return jsonify({
            "status": "unhealthy",
            "service": "model",
            "timestamp": time.time(),
            "message": "Model service is marked as unhealthy (simulated failure)"
        }), 503
    
    return jsonify({
        "status": "healthy",
        "service": "model",
        "timestamp": time.time(),
        "version": "1.0.0"
    })

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """Main sentiment analysis endpoint"""
    
    if not model_healthy:
        return jsonify({
            "error": "Model service is unhealthy",
            "message": "Sentiment analysis is temporarily unavailable"
        }), 503
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing required field 'text'",
                "message": "Request must contain 'text' field with review content"
            }), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({
                "error": "Empty text provided",
                "message": "Text field cannot be empty"
            }), 400
        
        if len(text) > 5000:
            return jsonify({
                "error": "Text too long",
                "message": "Text must be less than 5000 characters"
            }), 400
        
        # Analyze sentiment and generate rating
        result = analyze_sentiment_and_rating(text)
        
        # Add metadata
        result.update({
            "timestamp": time.time(),
            "text_length": len(text),
            "processed_by": "textblob"
        })
        
        print(f"📊 Analyzed: '{text[:50]}...' → {result['sentiment']} ({result['score']}) → {result['rating']} stars")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/admin/toggle-health', methods=['POST'])
def toggle_health():
    """Toggle model service health status for testing"""
    global model_healthy
    
    model_healthy = not model_healthy
    status = "healthy" if model_healthy else "unhealthy"
    
    print(f"🏥 Model service health toggled: {status.upper()}")
    
    return jsonify({
        "message": f"Model service marked as {status}",
        "healthy": model_healthy,
        "timestamp": time.time()
    })

@app.route('/admin/status', methods=['GET'])
def admin_status():
    """Get detailed service status for admin panel"""
    
    return jsonify({
        "service": "model",
        "healthy": model_healthy,
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime": time.time(),
        "capabilities": {
            "sentiment_analysis": True,
            "rating_generation": True,
            "supported_sentiments": ["positive", "negative", "neutral"]
        },
        "statistics": {
            "rating_ranges": {
                "positive": "4.0-5.0 stars",
                "neutral": "2.5-3.5 stars", 
                "negative": "1.0-2.0 stars"
            }
        }
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "Movie Review Sentiment Analysis API",
        "version": "1.0.0",
        "status": "healthy" if model_healthy else "unhealthy",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze",
            "admin_status": "GET /admin/status",
            "toggle_health": "POST /admin/toggle-health"
        },
        "example_request": {
            "url": "/analyze",
            "method": "POST",
            "body": {"text": "This movie was absolutely amazing!"}
        },
        "example_response": {
            "sentiment": "positive",
            "score": 0.625,
            "confidence": "high",
            "rating": 4.6,
            "timestamp": time.time()
        }
    })

if __name__ == '__main__':
    print("🤖 Starting Movie Review Sentiment Analysis Service")
    print(f"🌐 Model Server Port: {MODEL_PORT}")
    print("📊 Features: Sentiment Analysis + Rating Generation")
    print("🔧 Admin: Health toggle endpoint available")
    
    # Download required NLTK data if not present
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('brown', quiet=True)
        print("📚 NLTK data ready")
    except Exception as e:
        print(f"⚠️ NLTK setup warning: {e}")
    
    app.run(host='0.0.0.0', port=MODEL_PORT, debug=False) 