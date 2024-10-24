---
title: "Proyecto rendimiento de estudiantes"
author: "Leandro Soto Miranda"
date: "2024-10-07"
format: 
  html: 
    toc: true 
    code-fold: true
---

## 1. Definir problema

- En este proyecto, analizaremos un conjunto de datos de rendimiento de estudiantes con el objetivo de predecir el puntaje del examen de los estudiantes para generar un impacto en el rendimiento de los alumnos en el caso de que su rendimiento en los exámenes sea mejor compartiendo insights para la mejora del rendimiento del estudiante y se reduzca la posibilidad de desaprobar el examen.

## 2. Recopilación de datos

```{python}
# Importación de librerías
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import StackingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)


# Carga de datos
df = pd.read_csv('data.csv', sep=",")

# Resumen estadístico
# Mostrar las primeras filas del dataset
print("Primeras filas del dataset:")
print(df.head())

# Mostrar información general del dataset
print("\nInformación del dataset:")
print(df.info())

# Descripción estadística básica del dataset
print("\nDescripción estadística:")
print(df.describe())

info = df.shape
print("\nLa cantidad de filas y columnas en nuestro dataframe es de:",info)

tipos = df.dtypes
print("\nTipos de datos presentes en el dataset:\n",tipos)
```

## 3. Análisis de datos por Variable
## Análisis de datos cuantitativos

```{python}
# Función para el análisis univariado de variables cuantitativas
def analizar_variable_cuantitativa(df, columna):
    mean = np.mean(df[columna])
    median = np.median(df[columna])
    std = np.std(df[columna])
    min_value = np.min(df[columna])
    max_value = np.max(df[columna])

    print(f"Análisis de la Variable '{columna}'")
    print(f"Media: {mean:.2f}")
    print(f"Mediana: {median:.2f}")
    print(f"Desviación Estándar: {std:.2f}")
    print(f"Valor Mínimo: {min_value:.2f}")
    print(f"Valor Máximo: {max_value:.2f}")
    print("\n")

    # Visualización de la distribución (Histograma con KDE)
    plt.figure(figsize=(10, 6))
    sns.histplot(df[columna], bins=30, kde=True, color='#4C72B0')
    plt.title(f'Distribución de {columna}')
    plt.xlabel(columna)
    plt.ylabel('Frecuencia')
    plt.show()

# Aplicar la función a todas las columnas numéricas del dataframe
columnas_cuantitativas = df.select_dtypes(include=['int64', 'float64']).columns
for columna in columnas_cuantitativas:
    analizar_variable_cuantitativa(df, columna)
```

## Análisis de datos cualitativos

```{python}
# Función para el análisis univariado de variables categóricas
def analizar_variable_categorica(df, columna):
    values_counts = df[columna].value_counts()
    moda = values_counts.idxmax()

    print(f"Análisis Univariado de la Variable '{columna}'")
    print(f"Frecuencia de las categorías:\n{values_counts}")
    print(f"Moda (Categoría más frecuente): {moda}")
    print("\n")

    # Visualización de la distribución
    plt.figure(figsize=(10, 6))
    sns.countplot(
        x=columna, 
        data=df[df[columna].isin(values_counts.index)], 
        order=values_counts.index, 
        palette='Set2'
    )
    plt.title(f'Distribución de {columna}')
    plt.xlabel(columna)
    plt.ylabel('Frecuencia')
    plt.xticks(rotation=45)
    plt.show()

# Aplicar la función a todas las columnas categóricas del dataframe
columnas_categoricas = df.select_dtypes(include=['object']).columns
for columna in columnas_categoricas:
    analizar_variable_categorica(df, columna)

```

## Verificar si hay patrones o relaciones presentes entre variables
```{python}
sns.scatterplot(x='Hours_Studied', y='Exam_Score', data=df)
plt.title('Relación entre Horas de Estudio y Puntuación de Examen')
plt.xlabel('Horas de Estudio')
plt.ylabel('Puntuación de Examen')
plt.show()

```

```{python}
sns.scatterplot(x='Attendance', y='Exam_Score', data=df)
plt.title('Relación entre Horas de Estudio y Puntuación de Examen')
plt.xlabel('Horas de Estudio')
plt.ylabel('Puntuación de Examen')
plt.show()
```

## Verificar si hay valores nulos en el dataset
### Corrección de valores nulos presentes en el dataset
```{python}
print("\nValores nulos por columna:")
print(df.isnull().sum())
```
```{python}
# Lista de las columnas categóricas que deseas reemplazar por la moda
categorical_columns = ['Parental_Education_Level', 'Distance_from_Home', 'Teacher_Quality']

# Iterar sobre cada columna y reemplazar los valores nulos con la moda
for column in categorical_columns:
    mode_value = df[column].mode()[0]  # Obtener la moda (el valor más frecuente)
    df[column].fillna(mode_value, inplace=True)
    print(f"Valores nulos en '{column}' reemplazados por la moda: '{mode_value}'")

```

# Verificar si hay valores atípicos
```{python}
def generar_boxplot(df, columna):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x=columna, palette='Set2')
    plt.title(f'Boxplot de {columna}')
    plt.xlabel(columna)
    plt.show()

# Aplicar la función a todas las columnas numéricas del dataframe
columnas_numericas = df.select_dtypes(include=['int64', 'float64']).columns
for columna in columnas_numericas:
    generar_boxplot(df, columna)
```

- Para el tratamiento de datos atípicos lo que vamos a realizar es la imputación de ellos mediante el método intercuartílico, pero también vamos a generar un dataset sin realizar ningún tratamiento de los datos outlayers presentes en el dataset para realizar pruebas posteriormente en la aplicación de modelos de machine learning para ver cuanta diferencia hay entre ambos casos.
```{python}

df_clean = df.copy()

# Iteramos sobre cada columna numérica en el DataFrame.
for col in df_clean.select_dtypes(include=['int64', 'float64']).columns:
    # Calculamos el primer y tercer cuartil (Q1 y Q3)
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1  # Rango intercuartílico
    
    # Definimos los límites inferior y superior
    lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR

    # Imputamos los valores atípicos por los límites correspondientes
    df_clean[col] = np.where(df_clean[col] < lower_limit, lower_limit, df_clean[col])
    df_clean[col] = np.where(df_clean[col] > upper_limit, upper_limit, df_clean[col])

# Verificamos algunos valores antes y después de la limpieza
print("Datos antes de la limpieza:")
print(df.describe())
print("\nDatos después de la limpieza:")
print(df_clean.describe())
```

## Preparación de datos
### Vamos a realizar el tratamiento de datos pasos a realizar
### Convertir datos categóricos a numéricos para esto vamos a aplicar one hot encoder y label conder dependiendo a tipo de dato
### Además de convertir los datos categóricos en general para aplicar estos datos en modelos de machine learning, además de verificar el balanceo de datos y aplicación de técnicas para corregir variables con outlayers

```{python}
for column in df.columns:
    unique_values = df[column].unique()
    print(f"Valores únicos en la columna '{column}':")
    print(unique_values)
    print("\n------------------------------------\n")
```

## LabelEncoder
### Parental_Involvement, Access_to_Resources, Motivation_Level,Family_Income,Teacher_Quality,Peer_Influence,
```{python}
le = LabelEncoder()
df['Parental_Involvement'] = le.fit_transform(df['Parental_Involvement'].astype(str))

df['Access_to_Resources'] = le.fit_transform(df['Access_to_Resources'].astype(str))

df['Motivation_Level'] = le.fit_transform(df['Motivation_Level'].astype(str))

df['Family_Income'] = le.fit_transform(df['Family_Income'].astype(str))

df['Teacher_Quality'] = le.fit_transform(df['Teacher_Quality'].astype(str))

df['Peer_Influence'] = le.fit_transform(df['Peer_Influence'].astype(str))

df['Parental_Education_Level'] = le.fit_transform(df['Parental_Education_Level'].astype(str))

df['Distance_from_Home'] = le.fit_transform(df['Distance_from_Home'].astype(str))

# datos sin outlayers

df_clean['Parental_Involvement'] = le.fit_transform(df_clean['Parental_Involvement'].astype(str))

df_clean['Access_to_Resources'] = le.fit_transform(df_clean['Access_to_Resources'].astype(str))

df_clean['Motivation_Level'] = le.fit_transform(df_clean['Motivation_Level'].astype(str))

df_clean['Family_Income'] = le.fit_transform(df_clean['Family_Income'].astype(str))

df_clean['Teacher_Quality'] = le.fit_transform(df_clean['Teacher_Quality'].astype(str))

df_clean['Peer_Influence'] = le.fit_transform(df_clean['Peer_Influence'].astype(str))

df_clean['Parental_Education_Level'] = le.fit_transform(df_clean['Parental_Education_Level'].astype(str))

df_clean['Distance_from_Home'] = le.fit_transform(df_clean['Distance_from_Home'].astype(str))

```

## OneHotEncoder

### Internet_Access, Extracurricular_Activities, School_Type, Gender, ,Peer_Influence
```{python}
# Aplicar One-Hot Encoding
df = pd.get_dummies(df, columns=['Extracurricular_Activities'])
df = pd.get_dummies(df, columns=['Internet_Access'])
df = pd.get_dummies(df, columns=['School_Type'])
df = pd.get_dummies(df, columns=['Peer_Influence'])
df = pd.get_dummies(df, columns=['Learning_Disabilities'])
df = pd.get_dummies(df, columns=['Gender'])

# datos sin outlayers

df_clean = pd.get_dummies(df_clean, columns=['Extracurricular_Activities'])
df_clean = pd.get_dummies(df_clean, columns=['Internet_Access'])
df_clean = pd.get_dummies(df_clean, columns=['School_Type'])
df_clean = pd.get_dummies(df_clean, columns=['Peer_Influence'])
df_clean = pd.get_dummies(df_clean, columns=['Learning_Disabilities'])
df_clean = pd.get_dummies(df_clean, columns=['Gender'])
```

```{python}
for column in df.columns:
    unique_values = df[column].unique()
    print(f"Valores únicos en la columna '{column}':")
    print(unique_values)
    print("\n------------------------------------\n")
```


```{python}
# Calcular la matriz de correlación
corr_matrix = df.corr()

# Generar el mapa de calor
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Mapa de calor de la correlación entre variables')
plt.show()
```

```{python}
# Calcular la matriz de correlación
correlation_matrix = df.corr()

# Filtrar solo las correlaciones con la variable objetivo
target_corr = correlation_matrix['Exam_Score'].sort_values(ascending=False)
print("Correlación de cada variable con 'Exam_Score':\n", target_corr)
```

# Aplicación de modelos de machine learning

## Predicción con datos atípicos

```{python}
# Separar las características (X) y la variable objetivo (y)
X = df.drop(columns=['Exam_Score'])  # Todas las columnas excepto la variable objetivo
y = df['Exam_Score']  # La variable objetivo

# Dividir el conjunto de datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Lista de modelos de regresión para evaluar
models = {
    "Regresión Lineal": LinearRegression(),
    "Regresión Ridge": Ridge(alpha=1.0),
    "Regresión Lasso": Lasso(alpha=0.1),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42,),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
}
results = []

# Entrenar y evaluar cada modelo
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Almacenar los resultados
    results.append({
        "Modelo": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R^2": r2
    })

# Convertir los resultados en un DataFrame
results_df = pd.DataFrame(results)

# Mostrar los resultados ordenados por R^2
print(results_df.sort_values(by="R^2", ascending=False))

```
```{python}
# Variables utilizadas
print("Variables utilizadas en el modelo:")
print(X.columns)

```

```{python}

# Separar las variables independientes y la variable objetivo
X = df.drop(columns=['Exam_Score'])
y = df['Exam_Score']

# Dividir el conjunto de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Definir los modelos base
base_models = [
    ('linear', LinearRegression()),
    ('random_forest', RandomForestRegressor(n_estimators=100, random_state=42))
]

# Definir el modelo meta
meta_model = LinearRegression()

# Crear el Stacking Regressor
stacking_model = StackingRegressor(estimators=base_models, final_estimator=meta_model)

# Entrenar el modelo
stacking_model.fit(X_train, y_train)

# Hacer predicciones
y_pred = stacking_model.predict(X_test)

# Evaluar el modelo
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Mostrar resultados
print("Resultados del Stacking Regressor")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R^2: {r2:.4f}")
```


## Predicción sin datos atípicos
```{python}
# Separar las características (X) y la variable objetivo (y)
X = df_clean.drop(columns=['Exam_Score'])  # Todas las columnas excepto la variable objetivo
y = df_clean['Exam_Score']  # La variable objetivo

# Dividir el conjunto de datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Lista de modelos de regresión para evaluar
models = {
    "Regresión Lineal": LinearRegression(),
    "Regresión Ridge": Ridge(alpha=1.0),
    "Regresión Lasso": Lasso(alpha=0.1),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42,),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
}
results = []

# Entrenar y evaluar cada modelo
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Almacenar los resultados
    results.append({
        "Modelo": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R^2": r2
    })

# Convertir los resultados en un DataFrame
results_df = pd.DataFrame(results)

# Mostrar los resultados ordenados por R^2
print(results_df.sort_values(by="R^2", ascending=False))

```
```{python}
# Variables utilizadas
print("Variables utilizadas en el modelo:")
print(X.columns)

```

```{python}

# Separar las variables independientes y la variable objetivo
X = df_clean.drop(columns=['Exam_Score'])
y = df_clean['Exam_Score']

# Dividir el conjunto de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Definir los modelos base
base_models = [
    ('linear', LinearRegression()),
    ('random_forest', RandomForestRegressor(n_estimators=100, random_state=42))
]

# Definir el modelo meta
meta_model = LinearRegression()

# Crear el Stacking Regressor
stacking_model = StackingRegressor(estimators=base_models, final_estimator=meta_model)

# Entrenar el modelo
stacking_model.fit(X_train, y_train)

# Hacer predicciones
y_pred = stacking_model.predict(X_test)

# Evaluar el modelo
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Mostrar resultados
print("Resultados del Stacking Regressor")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R^2: {r2:.4f}")
```

## Comparación de métricas de modelos


### Comparación de resultados:

1. **Sin Datos Atípicos:**

- Los modelos mejoran su desempeño cuando los datos atípicos han sido ajustados.

Stacking Regressor tiene el mejor rendimiento con:

MAE: 0.8760 (error promedio bajo)

RMSE: 1.2578 (mejor precisión comparado con los otros modelos)

R²: 0.8588 (explica el 85.88% de la variabilidad en la variable objetivo)

  

- Random Forest y Regresión Ridge/Lineal presentan un desempeño similar en términos de MAE y RMSE, pero están ligeramente por debajo del Stacking Regressor.

- Regresión Lasso tiene un poco más de error en comparación con Ridge/Lineal.

- Árbol de Decisión muestra un rendimiento inferior con un MAE de 1.5109 y un R² de 0.6025, lo cual indica que no es tan eficaz en capturar la relación entre las variables.

  

2. **Con Datos Atípicos:**

- Los modelos se ven significativamente afectados por la presencia de outliers.

Stacking Regressor sigue siendo el mejor modelo en este caso, pero sus métricas son peores:

MAE: 0.9709

RMSE: 1.9767

R²: 0.7131 (una caída considerable comparada con el caso sin outliers, indicando que el modelo explica menos la variabilidad de la variable objetivo).

- Regresión Ridge/Lineal tienen un MAE de aproximadamente 1.008 y un RMSE de 2.016, indicando que los errores son mayores y su capacidad para predecir disminuye.

- Random Forest y Lasso también ven una degradación en su rendimiento.

- Árbol de Decisión se ve severamente afectado, con un R² cercano a 0, lo que sugiere que apenas explica la variabilidad de la variable objetivo.

  

### Conclusiones:

- Impacto de los Outliers: Los datos atípicos tienden a distorsionar las predicciones de los modelos, especialmente aquellos que no son robustos a valores extremos, como los árboles de decisión. Esto resulta en una mayor imprecisión (valores de MAE y RMSE más altos) y una menor capacidad de explicación (valores de R² más bajos).

- Importancia del Preprocesamiento: Ajustar los outliers ha mejorado el rendimiento de todos los modelos, especialmente del Stacking Regressor. Esto sugiere que los datos limpios permiten a los modelos captar mejor las relaciones entre las variables.