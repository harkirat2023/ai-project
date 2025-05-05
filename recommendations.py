import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

class MusicRecommender:
    def _init_(self, tracks_data):
        self.tracks = tracks_data
        self.scaler = StandardScaler()
        self._prepare_data()
        
    def _prepare_data(self):
        features = self.tracks['features'].str.split(expand=True)
        features.columns = ['bpm', 'danceability', 'energy', 'valence']
        features = features.astype(float)

        genres = self.tracks['genres'].str.get_dummies(sep=' ')

        self.feature_matrix = pd.concat([features, genres], axis=1)

        self.feature_matrix = pd.DataFrame(
            self.scaler.fit_transform(self.feature_matrix),
            columns=self.feature_matrix.columns
        )

        self.model = NearestNeighbors(n_neighbors=20, metric='cosine')
        self.model.fit(self.feature_matrix)
        
    def get_recommendations(self, user_history, num_recommendations=10):
        if not user_history:
            return self._get_fallback_recommendations(num_recommendations)

        history_df = pd.DataFrame(user_history, columns=['track_id', 'plays'])
        history_df['plays'] = history_df['plays'].fillna(1)

        listened_tracks = self.tracks[
            self.tracks['track_id'].isin(history_df['track_id'])
        ].merge(history_df, on='track_id')

        listened_features = self.feature_matrix.loc[listened_tracks.index]
        weights = listened_tracks['plays'].values
        user_profile = np.average(listened_features, axis=0, weights=weights)

        distances, indices = self.model.kneighbors(
            [user_profile], n_neighbors=num_recommendations+len(listened_tracks))
        recommendations = []
        for idx in indices[0]:
            track_id = self.tracks.iloc[idx]['track_id']
            if track_id not in listened_tracks['track_id'].values:
                recommendations.append(track_id)
                if len(recommendations) >= num_recommendations:
                    break
                    
        return recommendations
    
    def _get_fallback_recommendations(self, num_recommendations):
        return self.tracks.nlargest(num_recommendations, 'popularity')['track_id'].tolist()