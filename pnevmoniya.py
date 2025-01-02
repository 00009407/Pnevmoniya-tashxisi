# -*- coding: utf-8 -*-
"""Pnevmoniya.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cIpQ3LP4GjwPDQXJqxQpAv-_YMG7LNTT
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import zipfile

import os
!mkdir -p ~/.kaggle
!cp /content/kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle competitions download -c pnevmoniya

zip_file_path = "/content/pnevmoniya.zip"
extract_to = "/content/pnevmoniya/"

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print(f"Extracted files to {extract_to}")

# Ma'lumotlar papkasi yo'llari
train_dir = "/content/pnevmoniya/train"
test_dir = "/content/pnevmoniya/test"  # Faqat test tasvirlari bor papka

# Tasvir hajmi va partiya o'lchami
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Train va validatsiya uchun ma'lumotlar generatorlari
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2  # Validatsiya uchun 20%
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",  # Binary classification
    subset="training"
)

val_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation"
)

# ResNet50 bazasini yuklash
base_model = tf.keras.applications.ResNet50(
    weights='imagenet',  # Oldindan tayyorlangan og'irliklar
    include_top=False,   # Fully connected qatlamlarni olib tashlash
    input_shape=(224, 224, 3)
)

# Modelga yangi bosh qatlamlarni qo'shish
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dense(1, activation='sigmoid')(x)  # Ikki sinf uchun

# Modelni yaratish
model = Model(inputs=base_model.input, outputs=x)

# Oldingi qatlamlarni muzlatish
for layer in base_model.layers:
    layer.trainable = False

# Kompilyatsiya qilish
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Modelni o'qitish
EPOCHS = 20

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    validation_steps=val_generator.samples // BATCH_SIZE
)

# Oldingi qatlamlarni ochish
for layer in base_model.layers:
    layer.trainable = True

# Qayta kompilyatsiya qilish
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Modelni qayta o'qitish
fine_tune_epochs = 10
total_epochs = EPOCHS + fine_tune_epochs

history_fine = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=total_epochs,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    validation_steps=val_generator.samples // BATCH_SIZE,
    initial_epoch=EPOCHS
)

# Test tasvirlarini yuklash
test_images = []
image_names = []

for file_name in os.listdir(test_dir):
    if file_name.endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(test_dir, file_name)
        image = load_img(image_path, target_size=IMG_SIZE)
        image = img_to_array(image) / 255.0
        test_images.append(image)
        image_names.append(file_name)

# Test tasvirlarini numpy massiviga aylantirish
test_images = np.array(test_images)

# Bashorat qilish
predictions = model.predict(test_images)
predicted_classes = (predictions > 0.5).astype("int32")

# Natijalarni chop etish
for i, prediction in enumerate(predicted_classes):
    label = "Pneumonia" if prediction == 1 else "Normal"
    print(f"Image: {image_names[i]} -> Predicted Label: {label}")

# Tasvirlar va bashoratlarni ko'rsatish
plt.figure(figsize=(10, 10))
for i in range(min(9, len(test_images))):  # Faqat 9 tasvirni ko'rsatish
    plt.subplot(3, 3, i + 1)
    plt.imshow(test_images[i])
    label = "Pneumonia" if predicted_classes[i] == 1 else "Normal"
    plt.title(label)
    plt.axis("off")
plt.show()

# Yo'qotish va aniqlik grafigini chizish
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.title('Training and Validation Loss')
plt.show()

plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.title('Training and Validation Accuracy')
plt.show()

import pandas as pd

# Yuklangan faylni ko'rib chiqish
file_path = '/content/pnevmoniya/sample_solution.csv'
sample_solution = pd.read_csv(file_path)

# Faylning birinchi qatorlarini ko'rib chiqish
sample_solution.head()

# Tasvir nomlarini olib kelish
image_names = sample_solution['id'].tolist()

# Sinf natijalarini yaratish uchun tasodifiy bashoratlar
# (bu yerda haqiqiy model natijalarini qayerga kiritishni namoyish qilamiz)
# Tasavvur qiling, `predicted_classes` modeli bashoratlari
import numpy as np
predicted_classes = np.random.randint(0, 2, size=len(image_names))  # Tasodifiy bashorat (0 yoki 1)

# Natijalarni sample_solution formatiga kiritish
sample_solution['labels'] = predicted_classes

# Yangilangan faylni saqlash
output_path = '/content/pnevmoniya/sample_solution.csv'
sample_solution.to_csv(output_path, index=False)

output_path
