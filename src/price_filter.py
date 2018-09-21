# -*- coding: utf-8 -*-
#
#  price_filter.py
#  
#  Copyright 2018 Braian Hernan Vicente <bvicente@fi.uba.ar>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import pandas as pd
import numpy as np
    # Los datos fueron provistos por  http://www.properati.com.ar y
    # reorganizo en un solo dataset de la siguiente manera
    # https://github.com/BraianVicente/properati_argentina/blob/master/src/TP1%20-%20Properati%20-%20Parseo%20de%20datos%20por%20fecha.ipynb)


def property_filter_price(df):
    df['created_on'] = df['created_on'].apply(lambda x : pd.to_datetime(x))

    df['year'] = df['created_on'].apply(lambda x : x.year)

    df['year_month'] = df.created_on.apply(lambda x: str(x.year) + '-' + str(x.month))

    df['state_name'] = df.place_with_parent_names.apply(lambda x : x.split('|')[2])
    # Filtramos datos de CABA y GBA.
    df = df[
        (df['state_name'] == 'Bs.As. G.B.A. Zona Norte' ) |
        (df['state_name'] == 'Bs.As. G.B.A. Zona Sur' ) |
        (df['state_name'] == 'Bs.As. G.B.A. Zona Oeste' ) |
        (df['state_name'] == 'Capital Federal' )
        ]



    df['zone'] = df.place_with_parent_names.apply(lambda x : x.split('|')[3])

    #Filtramos por los datos que son reelevantes para nuestro analisis, ob-
    #teniendo unicamente las propiedades de GBA y capital federal


    df.drop(inplace=True,\
        labels=['country_name','description','extra','id',\
        'image_thumbnail','operation','place_with_parent_names_l1',\
        'place_with_parent_names_l2', 'properati_url','surface_in_m2',\
        'title'],axis=1)

    # Podemos seguir trabajando con los datos que no cuentan con la informa-
    # cion de Zona utilizando la ubicacion para identificarlos segun el ba-
    # rrio al que pertenecen pero en esta ocacion decidimos dejarlos de lado
    # pues no son una cantidad significativa de datos


    # Las propiedades del tigre son las unicas que no contienen informacion en 'place_name'

    df.loc[pd.isnull(df['place_name']),'place_name'] = df.place_name.\
        apply(lambda x : x if pd.notnull(x) else 'Tigre' )

    df = df[df['zone'] != '']


    # Se agrega la superficie total de los inmbuebles que disponen del
    # precio por metro cuadrado en USD y el precio aproximado en USD

    dataframe_calc_value(df,'surface_total_in_m2','price_aprox_usd','price_usd_per_m2')

    # Calculamos la superficie total en metros cuadrados de las propie-
    # dades que disponen del precio cuadrado en moneda actual y el precio
    # aproximado en moneda actual

    dataframe_calc_value(df,'surface_total_in_m2','price','price_per_m2')

    # Calculamos el precio por metro cuadrado en USD de los inmuebles
    # que cuentan con el precio aproximado en USD y la superficie total
    # en USD

    dataframe_calc_value(df,'price_usd_per_m2','price_aprox_usd','surface_total_in_m2')

    # Se agrega el precio por metro cuadrado en la moneda actual en cada
    # unos de las propiedades que disponen de la cantidad total de me-
    # tros cuadrados y el precio

    dataframe_calc_value(df,'price_per_m2','price','surface_total_in_m2')

    # Se va a quitar la informacion que puede afectar el analisis de
    # datos en los precios

    # Se quitan los datos que no cuenten con el precio o con la superfi-
    # cie total en metros cuadrados
    df = df[~((df['surface_total_in_m2'] == 0 ) | (df['price'] == 0 ))]

    # Vamos a filtrarlos datos que tengan precios entre entre USD 0 y
    # USD 4.500 por metro cuadrado
    # Filtraremos los datos que tengan entre 0 y 550.000
    # Filtraremos los datos que tengan una superficie total en metros
    # cuadrados entre 0 y 800



    df = df[(df['price_aprox_usd'] < 600000) & \
        (df['price_usd_per_m2'] < 5000) & \
        (df['surface_total_in_m2'] < 1000)]

    return df


def dataframe_calc_value(df,incognita,divisor,dividendo):
#Calcula el precio la incognita (incognita = divisor/dividendo) para todo divisor mayor a cero y todo dividendo mayor a cero.
    df.loc[ (pd.isnull(df[incognita])) |  (df[incognita] == 0 ) & \
        (pd.notnull(df[divisor]) ) & (df[divisor] > 0) & \
        (pd.notnull(df[dividendo]) & (df[dividendo] > 0)) ,incognita] = \
    df.loc[ (pd.isnull(df[incognita])) |  (df[incognita] == 0 ) & \
        (pd.notnull(df[divisor]) ) & (df[divisor] > 0) & \
        (pd.notnull(df[dividendo]) & (df[dividendo] > 0))][divisor] / \
    df.loc[ (pd.isnull(df[incognita])) |  (df[incognita] == 0 ) &\
        (pd.notnull(df[divisor]) ) & (df[divisor] > 0) & \
        (pd.notnull(df[dividendo]) & (df[dividendo] > 0))][dividendo]
