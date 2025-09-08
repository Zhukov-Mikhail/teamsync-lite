import pandas as pd
import numpy as np
from textblob import TextBlob
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

def analyze_team_communication(csv_path):
    """
    Анализирует коммуникационные данные команды из CSV файла
    Формат CSV: date,channel,member,message
    """
    # Загружаем данные
    df = pd.read_csv(csv_path)
    
    # Очищаем данные
    df = df.dropna(subset=['message'])
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. Анализ частоты коммуникаций
    daily_activity = df.set_index('date').resample('D').size()
    avg_daily_messages = round(daily_activity.mean(), 1)
    
    # 2. Анализ тональности
    def get_sentiment(text):
        try:
            return TextBlob(str(text)).sentiment.polarity
        except:
            return 0
    
    df['sentiment'] = df['message'].apply(get_sentiment)
    avg_sentiment = round(df['sentiment'].mean(), 2)
    
    # 3. Анализ баланса участия
    participation = df['member'].value_counts(normalize=True)
    participation_balance = 1 - participation.std()
    participation_balance = round(participation_balance * 100, 1)
    
    # Вычисляем общий балл
    communication_score = min(100, max(0, avg_daily_messages * 2))
    sentiment_score = min(100, max(0, (avg_sentiment + 1) * 50))
    balance_score = min(100, max(0, participation_balance))
    
    total_score = round((communication_score * 0.4 + 
                         sentiment_score * 0.3 + 
                         balance_score * 0.3), 1)
    
    # Генерируем рекомендации
    recommendations = []
    if avg_daily_messages < 5:
        recommendations.append("⚠️ Низкая частота коммуникаций. Рекомендуется ввести ежедневные 15-минутные стендапы.")
    if avg_sentiment < 0.1:
        recommendations.append("⚠️ Нейтральный/негативный тон обсуждений. Попробуйте начинать встречи с позитивных моментов.")
    if participation.std() > 0.3:
        recommendations.append("⚠️ Неравномерное участие. Внедрите систему ротации ведущего встреч.")
    
    if not recommendations:
        recommendations.append("✅ Отличный баланс коммуникаций! Продолжайте в том же духе.")
    
    # Создаем простой отчет
    report = {
        "total_score": total_score,
        "metrics": {
            "communication": {
                "value": avg_daily_messages,
                "score": communication_score,
                "label": f"{avg_daily_messages} сообщений/день"
            },
            "sentiment": {
                "value": avg_sentiment,
                "score": sentiment_score,
                "label": "Позитивный" if avg_sentiment > 0.2 else "Нейтральный" if avg_sentiment > -0.1 else "Негативный"
            },
            "balance": {
                "value": participation_balance,
                "score": balance_score,
                "label": f"{participation_balance}% баланса"
            }
        },
        "recommendations": recommendations,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    return report

def generate_html_report(report, output_path="report.html"):
    """Генерирует HTML отчет"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TeamSync Lite Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .score-container {{ text-align: center; margin: 30px 0; }}
            .score {{ font-size: 72px; font-weight: bold; color: {'#2e7d32' if report['total_score'] > 70 else '#ed6c02' if report['total_score'] > 50 else '#c62828'}; }}
            .metric {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
            .metric-name {{ font-weight: bold; margin-bottom: 5px; }}
            .metric-bar {{ height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }}
            .metric-fill {{ height: '100%'; width: {report['metrics']['communication']['score']}%; background: #1976d2; display: inline-block; }}
            .recommendations {{ background: #e8f5e9; padding: 15px; border-radius: 8px; }}
            .recommendation-item {{ margin: 10px 0; }}
            .date {{ text-align: right; color: #666; font-size: 0.8em; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>TeamSync Lite Report</h1>
            <p>Анализ коммуникаций гибридной команды</p>
        </div>
        
        <div class="score-container">
            <div class="score">{report['total_score']}/100</div>
            <p>Общий балл синергии команды</p>
        </div>
        
        <div class="metric">
            <div class="metric-name">Частота коммуникаций</div>
            <div>{report['metrics']['communication']['label']}</div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: {report['metrics']['communication']['score']}%"></div>
            </div>
        </div>
        
        <div class="metric">
            <div class="metric-name">Тон обсуждений</div>
            <div>{report['metrics']['sentiment']['label']}</div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: {report['metrics']['sentiment']['score']}%"></div>
            </div>
        </div>
        
        <div class="metric">
            <div class="metric-name">Баланс участия</div>
            <div>{report['metrics']['balance']['label']}</div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: {report['metrics']['balance']['score']}%"></div>
            </div>
        </div>
        
        <div class="recommendations">
            <h2>Рекомендации</h2>
            {''.join([f'<div class="recommendation-item">• {rec}</div>' for rec in report['recommendations']])}
        </div>
        
        <div class="date">Отчет сгенерирован: {report['date']}</div>
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        report = analyze_team_communication(sys.argv[1])
        generate_html_report(report)
        print(f"Отчет успешно сгенерирован! Общий балл: {report['total_score']}/100")
    else:
        print("Использование: python team_analysis.py путь_к_файлу.csv")
