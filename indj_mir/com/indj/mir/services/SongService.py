from indj_mir.com.indj.mir.respository import SongsRepository


def get_unique_genre():
    genres = SongsRepository.get_genres()
    uniqueGenre = set([])
    for genre in genres:
        if 'rhythm & blues' in genre:
            genre = genre.replace('rhythm & blues', 'r&b')
        if 'Electronica' in genre:
            genre = genre.replace('Electronica', 'electronic')

        if '/' not in genre and ',' not in genre and '-' not in genre:
            uniqueGenre.add(genre.lower())
        else:
            if '/' in genre:
                specificGenre = [x.strip() for x in genre.split('/')]
                uniqueGenre |= normalized_genre(specificGenre)
            if ',' in genre:
                specificGenre = [x.strip() for x in genre.split(',')]
                uniqueGenre |= normalized_genre(specificGenre)

    print('unique_genre:', uniqueGenre)
    return uniqueGenre


def normalized_genre(genres):
    uniqueGenre = set([])
    for genreItem in genres:
        item = genreItem
        if '-' in item:
            item = item.replace('-', '')
        uniqueGenre.add(item.lower())
    return uniqueGenre