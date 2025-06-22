# Speech Emotion Recognition

## Overview
A quick summary of the project is provided below. For a complete description of working and functionality, please refer to the attached detailed report.

# Summary
In this project, multiple machine learning and deep learning models were explored and evaluated 
to identify the most effective approach for classifying emotions from speech signals. The following 
models were considered:  
## Random Forest Classifier (RFC): Random Forest is an ensemble learning method based on 
decision trees. It operates by constructing multiple decision trees during training and outputting 
the class that is the mode of the classes predicted by individual trees.  
Why considered:  
• Robust to overfitting.  
• Handles high-dimensional feature spaces well.  
• Easy to implement and interpret.  

## Support Vector Machine (SVM): SVM is a powerful supervised learning algorithm for  
classification tasks, aiming to find the optimal hyperplane that separates different classes in a 
highdimensional space.  
Why considered:  
• Effective in small to medium-sized datasets.  
• Works well with clear margin of separation.  

## Convolutional Neural Networks (CNN) Neural Network: CNN is a type of Recurrent Neural Network (RNN) 
designed to learn long-term dependencies in sequential data by maintaining memory cells and gating 
mechanisms to control information flow.  
Why chosen:  
• Captures temporal dependencies: Unlike RFC and SVM, CNN extracts spatial features from audio 
representations, making it ideal for speech analysis.  
• Handles variable-length sequences: Suitable for audio data where speech patterns unfold 
over time.  
• Learns contextual patterns: Effectively recognizes patterns in pitch, tone, and intensity 
variations, crucial for emotion classification.  
Performance:  
The CNN model consistently outperformed Random Forest and SVM in terms of:  
• Accuracy  
• Precision, Recall, F1-score  
• Generalization to unseen speech samples  
It demonstrated superior ability to distinguish between subtle emotional states like fear and sad, 
or surprise and happy, which other models struggled with.
