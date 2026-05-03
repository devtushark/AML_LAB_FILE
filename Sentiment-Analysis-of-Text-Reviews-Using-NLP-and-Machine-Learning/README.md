# Sentiment Analysis of Text Reviews Using NLP and Machine Learning

![](sentiment_analysis_img.jpg)

## Project Description
This project focuses on performing sentiment analysis on a large dataset of text reviews. The primary goal is to classify reviews into three categories: Positive, Negative, and Neutral, based on their textual content. Using Natural Language Processing (NLP) and Machine Learning, the project showcases the complete pipeline from data preprocessing to model evaluation.

## Features
- **Dataset**: A labeled dataset of text reviews with sentiment categories.
- **Data Preprocessing**:
  - Handling missing values.
  - Text vectorization using TF-IDF.
  - Splitting data into training and testing sets.
- **Model Implementation**: Multinomial Naive Bayes for efficient text classification.
- **Evaluation Metrics**:
  - Accuracy Score
  - Classification Report
  - Confusion Matrix with Heatmap Visualization
- **Insights**:
  - Analysis of model performance and suggestions for improvement.

## Steps in the Project
1. **Data Loading**:
   - Read and explore the dataset.
   - Check for missing values and clean the data.

2. **Data Preprocessing**:
   - Vectorize text data using TF-IDF to extract important features.
   - Split the dataset into training (80%) and testing (20%) sets.

3. **Model Training**:
   - Use the Multinomial Naive Bayes algorithm due to its effectiveness for text classification tasks.

4. **Model Evaluation**:
   - Evaluate model performance using accuracy, precision, recall, and F1-score.
   - Visualize results using a confusion matrix heatmap.

5. **Insights**:
   - Highlight key findings from the model's performance.

## Usage
Run the notebook to execute all steps from data loading to model evaluation:
```bash
https://colab.research.google.com/drive/1jH7EHhAPHclytqhzQzmcQ2C6AraJbgS3#scrollTo=wV3zB5cVMgH_
```

## Results
The project achieved a high accuracy score, showcasing the effectiveness of the preprocessing and modeling techniques used. The confusion matrix highlights areas for potential improvement.

## Technologies Used
- Python
- Scikit-learn
- Pandas
- Matplotlib
- Seaborn

## Contributing
Contributions are welcome! If you'd like to improve this project, please fork the repository and submit a pull request.

## Acknowledgments
- Special thanks to the open-source community for providing excellent tools and libraries for NLP and machine learning.
