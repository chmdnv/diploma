import joblib
import pandas as pd
import math
from geo_request import get_coords
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import os


def get_daytime(dt) -> str:
    if 0 <= dt.hour < 6:
        return 'night'
    elif 6 <= dt.hour < 12:
        return 'morning'
    elif 12 <= dt.hour < 18:
        return 'afternoon'
    elif 18 <= dt.hour:
        return 'evening'


def get_total_pixels(res: str) -> int:
    pixels = int(int.__mul__(*map(int, res.split('x'))))
    return math.log(pixels, 10) if pixels else 0


def get_screen_aspect(res: str) -> float:
    aspect = 1 / int.__truediv__(*map(int, res.split('x')))
    return round(aspect, 1)


def predict_custom(pred_probs, trsh: float = 0.5) -> list[int]:
    return [(0 if p1 < trsh else 1) for p0, p1 in pred_probs]


def add_new_features(data: pd.DataFrame) -> pd.DataFrame:
    data['visit_dt'] = pd.to_datetime(data['visit_date'] + ' ' + data['visit_time'])
    data.drop(columns=['visit_date', 'visit_time'], inplace=True)
    data['dayofweek'] = data.visit_dt.dt.day_name()
    data['daytime'] = data.visit_dt.apply(get_daytime)
    data['pixels'] = data.device_screen_resolution.apply(get_total_pixels)
    data['screen_aspect'] = data.device_screen_resolution.apply(get_screen_aspect)

    data['device_browser'] = data.device_browser.apply(lambda x: x.split()[0])
    browsers = ('Chrome', 'Safari', 'YaBrowser', 'Samsung', 'Android', 'Opera', 'Firefox', 'Edge')
    data['device_browser'] = data.device_browser.apply(
        lambda x:
        x if x in browsers
        else 'other'
    )

    # load coordinates for cities
    coords = joblib.load('data/coords.pkl')

    moscow = coords['Moscow']  # 55.75222, 37.61556
    data.geo_city = data.geo_city.apply(lambda x: x if x in coords else get_coords(x))
    data['dist_to_msk'] = data.geo_city.apply(
        lambda x: math.sqrt((coords[x][0] - moscow[0]) ** 2 + (coords[x][1] - moscow[1]) ** 2))

    # drop useless
    data = data.drop(columns=['visit_dt', 'session_id', 'client_id', 'geo_country',
                              'device_screen_resolution', 'device_model'])

    return data


def prepare_ohe(data: pd.DataFrame, ohe: OneHotEncoder) -> pd.DataFrame:
    """replace categories not to be seen in ohe with 'other'"""
    for i, col in enumerate(ohe.feature_names_in_):
        data[col] = data[col].apply(lambda x: x if x in ohe.categories_[i] else 'other')
    return data


def make_prediction(df: pd.DataFrame) -> list[int]:
    # new features
    df = add_new_features(df)

    # numerical encoding
    num_feat = df[['visit_number', 'dist_to_msk', 'pixels', 'screen_aspect']]
    std_scaler = StandardScaler()
    std_scaler.fit(num_feat)
    scaled = std_scaler.transform(num_feat)
    feat_title = [f"{title}_std" for title in num_feat.columns]
    df[feat_title] = scaled
    df.drop(columns=num_feat.columns, inplace=True)

    # заменим в категориальных фичах все '(not set)' и '(none)' значением 'other'
    for feat in df.columns:
        df[feat] = df[feat].mask(
            lambda x: x.isin(('(not set)', '(none)')),
            'other'
        )

    # categorical encoding - OHE
    cat_feat = df[['utm_source', 'utm_medium', 'utm_campaign', 'utm_adcontent',
                   'utm_keyword', 'device_category', 'device_os', 'device_brand',
                   'device_browser', 'geo_city', 'dayofweek', 'daytime',
                   ]].astype('category')

    ohe = joblib.load('data/ohe.pkl')
    cat_feat = prepare_ohe(cat_feat, ohe)
    ohe_cat = ohe.transform(cat_feat)

    df_result = pd.concat([df.drop(columns=cat_feat.columns),
                           pd.DataFrame(index=df.index,
                                        data=ohe_cat,
                                        columns=ohe.get_feature_names_out()
                                        )
                           ],
                          axis=1
                          )

    # choose the latest version of a model
    model_file_name = max([file for file in os.listdir('model') if file.endswith('.pkl')])
    # load the model from pickle
    model_meta = joblib.load(f'model/{model_file_name}')
    model = model_meta['model']
    trsh = model_meta['optimal_trsh']

    # make a prediction with an optimal threshold
    pred_hgb = predict_custom(model.predict_proba(df_result), trsh=trsh)

    return pred_hgb


def main():
    data = pd.read_json('data/data_for_test.json',
                        orient='records',
                        convert_dates=False,
                        # dtype={'visit_date': str, 'visit_time': str}
                        )
    target = make_prediction(data.sample())
    # target = make_prediction(data.iloc[0:1, :].copy())
    print(f"{target=}")


if __name__ == '__main__':
    main()
