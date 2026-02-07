import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Required for Django server-side rendering
import matplotlib.pyplot as plt
import io
import base64

def process_data(file_obj, threshold_ratio=0.5):
    # 1. Data Ingestion
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        return None

    # 2. Compute Complaint Density (Normalized per 1000 people)
    # This allows fair comparison between small villages and large cities.
    df['density'] = (df['complaints'] / df['population']) * 1000
    
    # 3. Analytics: Summary Stats
    mean_density = df['density'].mean()
    median_density = df['density'].median()
    
    # 4. Statistical Anomaly Detection (Z-Score)
    # Measures how many standard deviations a district is from the "Baseline of Normalcy."
    std_dev = df['density'].std()
    if std_dev == 0 or np.isnan(std_dev):
        df['density_z'] = 0
    else:
        df['density_z'] = (df['density'] - mean_density) / std_dev
    
    # 5. Flagging Rules
    # Districts falling below the threshold are flagged as "Silent Zones."
    cutoff = mean_density * float(threshold_ratio)
    df['is_silent'] = df['density'] < cutoff
    
    # 6. Trend Gap (Fear Indicator) Logic
    # A Trend Gap occurs when a region that used to report (history_avg) suddenly drops.
    df['trend_gap'] = df['history_avg'] - df['complaints']
    
    # The fear_score identifies where silence is likely due to suppression.
    df['fear_score'] = np.where(
        (df['is_silent']) & (df['history_avg'] > mean_density), 
        (df['trend_gap'] / df['population']) * 100, 
        0
    )

    # 7. Visualization: The Silence Map
    # Dark theme styling to match your dashboard UI.
    plt.figure(figsize=(10, 6), facecolor='#162a45')
    ax = plt.gca()
    ax.set_facecolor('#162a45')
    
    # Plot Standard Districts (Blue)
    normal = df[~df['is_silent']]
    if not normal.empty:
        plt.scatter(normal['population'], normal['complaints'], 
                    color='#4C6A85', alpha=0.5, s=60, label='Standard Reporting')
    
    # Plot Silent Zones (Orange/Red)
    silent = df[df['is_silent']]
    if not silent.empty:
        plt.scatter(silent['population'], silent['complaints'], 
                    color='#D97742', s=120, edgecolors='#f5d48c', 
                    linewidth=2, label='Flagged Silence', zorder=5)

    # Chart Formatting
    plt.title('Systemic Silence Map', color='#f5d48c', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Population Size', color='#cbd5e1')
    plt.ylabel('Complaint Volume', color='#cbd5e1')
    
    # Customize axes colors
    ax.tick_params(colors='#cbd5e1')
    for spine in ax.spines.values():
        spine.set_color('#4C6A85')
    
    plt.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
    plt.legend(facecolor='#1F3A5F', edgecolor='#4C6A85', labelcolor='#ffffff')
    
    # Save to Buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#162a45')
    plt.close()
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # 8. AI Insights Generation
    flagged_count = int(len(silent))
    trend_gaps = int(len(df[df['fear_score'] > 0]))
    insights = (
        f"Analysis complete. Found {flagged_count} silent zones. "
        f"Critical: {trend_gaps} regions show a 'Trend Gap,' suggesting potential data suppression."
    )

    # 9. Final Payload for HTML
    return {
        'chart': chart_data,
        'stats': {
            'mean': round(float(mean_density), 2),
            'median': round(float(median_density), 2),
            'flagged_count': flagged_count
        },
        'ranked_regions': silent.sort_values(by='fear_score', ascending=False).to_dict('records'),
        'ai_insights': insights
    }