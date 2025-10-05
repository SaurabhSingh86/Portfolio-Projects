# 🫁 Pneumonia Detection Using Deep Learning

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

> An AI-powered pneumonia detection system that compares 6 deep learning models with explainable predictions, real-time inference, and an interactive web interface.

[**🎥 Watch Demo Video**](YOUR_YOUTUBE_LINK) | [**📊 View Live Demo**](YOUR_LIVE_DEMO_LINK) | [**📄 Read Documentation**](#documentation)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Models Performance](#models-performance)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Results](#results)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

Pneumonia kills a child every 43 seconds worldwide (WHO, 2019). This project addresses the critical need for faster, accurate pneumonia diagnosis by leveraging deep learning to analyze chest X-rays.

**What makes this project unique:**

- ✅ **6 AI Models** compared side-by-side (Custom CNN, Fine-tuned CNN, ResNet50, MobileNetV2, DenseNet121, YOLOv5)
- ✅ **Explainable AI** with YOLOv5 bounding box visualization showing infected lung regions
- ✅ **Production-ready** FastAPI backend with async processing
- ✅ **Interactive UI** built with Streamlit for easy model comparison
- ✅ **Real-time predictions** with adjustable confidence thresholds
- ✅ **Feedback system** for continuous model improvement

---

## ✨ Key Features

### 🔬 Multi-Model Comparison

- Custom CNN (baseline)
- Fine-tuned CNN
- ResNet50 (transfer learning)
- MobileNetV2 (optimized for mobile)
- DenseNet121 (dense connections)
- YOLOv5 (object detection with visualization)

### 🎨 Interactive Web Interface

- Upload chest X-rays (JPG/PNG/DICOM formats)
- Select from 6 different AI models
- Adjustable sensitivity threshold
- Color-coded results (Green = Normal, Red = Pneumonia)
- User feedback collection
- Download predictions as CSV

### 🔍 Explainable AI

- YOLOv5 provides bounding boxes showing exact infected lung regions
- Confidence scores for all predictions
- Model-wise performance tracking

### ⚡ Production-Ready Architecture

- FastAPI REST API for scalable backend
- Async processing for real-time inference
- Auto-generated API documentation
- Easy integration with hospital systems

---

## 🏗️ System Architecture
