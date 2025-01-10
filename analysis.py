import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')

# Read the CSV files
health_data = pd.read_csv('health_metrics.csv')
weather_data = pd.read_csv('weather_data.csv')

# Convert date columns to datetime
health_data['date'] = pd.to_datetime(health_data['date'])
weather_data['time'] = pd.to_datetime(weather_data['time'])

# Add weather codes mapping early
weather_codes = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    71: 'Slight snow',
    73: 'Moderate snow'
}

# Merge the datasets
merged_data = pd.merge(
    health_data,
    weather_data,
    left_on='date',
    right_on='time',
    how='inner'
)

# Add weather descriptions
merged_data['weather_description'] = merged_data['weathercode'].map(weather_codes)

# Add weekday column
merged_data['weekday'] = merged_data['date'].dt.day_name()

# Add season column
merged_data['season'] = merged_data['date'].dt.month.map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Fall', 10: 'Fall', 11: 'Fall'
})

# Create 'analysis_results.txt' for storing statistics
with open('analysis_results.txt', 'w') as f:
    # Write basic statistics
    f.write("=== Health and Weather Analysis Results ===\n\n")
    f.write("Health Metrics Summary:\n")
    f.write(health_data[['steps', 'calories', 'km']].describe().to_string())
    f.write("\n\nWeather Summary:\n")
    f.write(weather_data[['temperature_2m_max', 'precipitation_sum', 'windspeed_10m_max']].describe().to_string())
    
    # Monthly averages
    merged_data['month'] = merged_data['date'].dt.month
    monthly_stats = merged_data.groupby('month').agg({
        'steps': 'mean',
        'temperature_2m_max': 'mean',
        'precipitation_sum': 'mean'
    }).round(2)
    
    f.write("\n\nMonthly Averages:\n")
    f.write(monthly_stats.to_string())
    
    # Top Activity Days
    f.write("\n\nTop 5 Most Active Days:\n")
    top_days = merged_data.nlargest(5, 'steps')[['date', 'steps', 'weather_description', 'temperature_2m_max']]
    f.write(top_days.to_string())
    
    # Weekly Patterns
    weekly_stats = merged_data.groupby('weekday').agg({
        'steps': ['mean', 'std', 'count']
    }).round(2)
    weekly_stats = weekly_stats.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    f.write("\n\nWeekly Activity Patterns:\n")
    f.write(weekly_stats.to_string())
    
    # Seasonal Analysis
    seasonal_stats = merged_data.groupby('season').agg({
        'steps': ['mean', 'std'],
        'km': 'mean',
        'calories': 'mean'
    }).round(2)
    f.write("\n\nSeasonal Activity Patterns:\n")
    f.write(seasonal_stats.to_string())
    
    # Weather Impact Analysis
    weather_impact = merged_data.groupby('weather_description').agg({
        'steps': ['mean', 'count'],
        'km': 'mean'
    }).round(2)
    f.write("\n\nActivity by Weather Condition:\n")
    f.write(weather_impact.to_string())
    
    # Achievement Statistics
    f.write("\n\nAchievement Statistics:")
    f.write(f"\n- Days with >10,000 steps: {len(merged_data[merged_data['steps'] > 10000])}")
    f.write(f"\n- Average steps on weekdays: {merged_data[merged_data['weekday'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]['steps'].mean():.0f}")
    f.write(f"\n- Average steps on weekends: {merged_data[merged_data['weekday'].isin(['Saturday', 'Sunday'])]['steps'].mean():.0f}")
    
    # Temperature Impact
    temp_correlation = merged_data['steps'].corr(merged_data['temperature_2m_max'])
    f.write(f"\n\nTemperature Impact:")
    f.write(f"\n- Correlation between temperature and steps: {temp_correlation:.3f}")
    
    # Streak Analysis
    streak_threshold = 10000  # Define what constitutes an "active" day
    active_days = merged_data['steps'] > streak_threshold
    current_streak = 0
    max_streak = 0
    
    for is_active in active_days:
        if is_active:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
            
    f.write(f"\n\nStreak Analysis:")
    f.write(f"\n- Longest streak of {streak_threshold}+ steps: {max_streak} days")
    
    # Time-based Analysis
    f.write("\n\nTime-based Patterns:")
    f.write(f"\n- Most active month: {monthly_stats['steps'].idxmax()} ({monthly_stats['steps'].max():.0f} avg steps)")
    f.write(f"\n- Most active season: {seasonal_stats['steps']['mean'].idxmax()} ({seasonal_stats['steps']['mean'].max():.0f} avg steps)")
    f.write(f"\n- Most active day of week: {weekly_stats['steps']['mean'].idxmax()} ({weekly_stats['steps']['mean'].max():.0f} avg steps)")

# 1. Original correlation heatmap
plt.figure(figsize=(12, 8))
numerical_columns = ['steps', 'calories', 'km', 'temperature_2m_max', 'temperature_2m_min',
                    'precipitation_sum', 'rain_sum', 'windspeed_10m_max', 'sunshine_duration']
correlation_matrix = merged_data[numerical_columns].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='magma', center=0,
            annot_kws={'size': 8}, fmt='.2f')
plt.title('Correlation Matrix of Health Metrics and Weather Data', pad=20)
plt.tight_layout()
plt.savefig('visualizations/1_correlation_heatmap.png')
plt.close()

# 2. Steps distribution by season (Box Plot)
plt.figure(figsize=(12, 6))
sns.set_palette("husl")
sns.boxplot(x='season', y='steps', data=merged_data, 
            order=['Spring', 'Summer', 'Fall', 'Winter'],
            palette='plasma')
plt.title('Distribution of Daily Steps by Season', pad=15)
plt.savefig('visualizations/2_steps_by_season.png')
plt.close()

# 3. Monthly trends
monthly_avg = merged_data.groupby('month')[['steps', 'temperature_2m_max']].mean()
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

# Using more vibrant colors and adding style
ax1.plot(monthly_avg.index, monthly_avg['steps'], color='#FF6B6B', label='Steps',
         linewidth=2.5, marker='o', markersize=8)
ax2.plot(monthly_avg.index, monthly_avg['temperature_2m_max'], color='#4ECDC4', 
         label='Temperature', linewidth=2.5, marker='s', markersize=8)

ax1.set_xlabel('Month')
ax1.set_ylabel('Average Steps', color='#FF6B6B', fontsize=10)
ax2.set_ylabel('Average Temperature (°C)', color='#4ECDC4', fontsize=10)
plt.title('Monthly Trends: Steps vs Temperature', pad=15)

# Add legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.savefig('visualizations/3_monthly_trends.png')
plt.close()

# 4. Steps vs Sunshine Duration
plt.figure(figsize=(10, 6))
plt.style.use('seaborn-v0_8-darkgrid')
scatter = plt.scatter(merged_data['sunshine_duration']/3600, 
                     merged_data['steps'], 
                     alpha=0.6,
                     c=merged_data['temperature_2m_max'],
                     cmap='viridis',
                     s=100)
plt.colorbar(scatter, label='Temperature (°C)')
plt.xlabel('Sunshine Duration (hours)')
plt.ylabel('Steps')
plt.title('Daily Steps vs Sunshine Duration\nColor = Temperature', pad=15)
plt.savefig('visualizations/4_steps_vs_sunshine.png')
plt.close()

# 5. Weekly patterns
merged_data['weekday'] = merged_data['date'].dt.day_name()
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
plt.figure(figsize=(12, 6))
sns.boxplot(x='weekday', y='steps', data=merged_data, 
            order=weekday_order,
            palette='rocket',
            width=0.7)
plt.xticks(rotation=45)
plt.title('Steps Distribution by Day of Week', pad=15)
plt.tight_layout()
plt.savefig('visualizations/5_weekly_patterns.png')
plt.close()

# 6. Activity levels vs Weather conditions (Enhanced version)
plt.figure(figsize=(14, 7))
sns.set_palette("husl")
sns.boxenplot(x='weather_description', y='steps', data=merged_data, 
              palette='viridis', width=0.7)
plt.xticks(rotation=45, ha='right')
plt.xlabel('Weather Condition')
plt.ylabel('Steps')
plt.title('Activity Levels by Weather Condition', pad=20)
plt.tight_layout()
plt.savefig('visualizations/6_activity_vs_weather.png')
plt.close()

# 7. Calories vs Steps relationship
plt.figure(figsize=(10, 6))
sns.regplot(x='steps', y='calories', data=merged_data, scatter_kws={'alpha':0.5})
plt.title('Relationship between Steps and Calories Burned')
plt.savefig('visualizations/7_calories_vs_steps.png')
plt.close()

# 8. Monthly distance covered
plt.figure(figsize=(12, 6))
monthly_distance = merged_data.groupby('month')['km'].mean()
monthly_distance.plot(kind='bar')
plt.title('Average Distance Covered by Month')
plt.xlabel('Month')
plt.ylabel('Average Distance (km)')
plt.tight_layout()
plt.savefig('visualizations/8_monthly_distance.png')
plt.close()

# 9. Steps Heatmap by Hour and Day
plt.figure(figsize=(15, 8))
merged_data['hour'] = merged_data['date'].dt.hour
merged_data['day_of_week'] = merged_data['date'].dt.day_name()
daily_hour_steps = merged_data.pivot_table(
    values='steps', 
    index='day_of_week',
    columns='month',
    aggfunc='mean'
)
sns.heatmap(daily_hour_steps, 
            cmap='RdYlBu_r',
            center=daily_hour_steps.mean().mean(),
            annot=True, 
            fmt='.0f',
            cbar_kws={'label': 'Average Steps'})
plt.title('Average Steps by Day and Month')
plt.xlabel('Month')
plt.ylabel('Day of Week')
plt.tight_layout()
plt.savefig('visualizations/9_steps_heatmap.png')
plt.close()

# 10. Weather Impact on Activity (Bubble Plot)
plt.figure(figsize=(12, 8))
plt.style.use('seaborn-v0_8-darkgrid')
scatter = plt.scatter(merged_data['temperature_2m_max'], 
                     merged_data['steps'],
                     c=merged_data['precipitation_sum'],
                     s=merged_data['windspeed_10m_max']*20,
                     alpha=0.6,
                     cmap='viridis')
plt.colorbar(scatter, label='Precipitation (mm)')
plt.xlabel('Maximum Temperature (°C)')
plt.ylabel('Daily Steps')
plt.title('Weather Impact on Activity\nBubble Size = Wind Speed')
plt.tight_layout()
plt.savefig('visualizations/10_weather_impact_bubble.png')
plt.close()

print("Analysis complete! Results have been saved to 'analysis_results.txt'")
print("Visualizations have been saved to the 'visualizations' directory") 