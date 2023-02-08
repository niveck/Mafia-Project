from csv import writer
from train.demonstrate import load_game_from_csv, Demonstrator

def evaluate_on_game(model_path, dataset_path, game_id):
    model = Demonstrator(model_path)
    sample_list = load_game_from_csv(dataset_path, game_id)

    preds = []
    for source, _ in sample_list:
        if source.strip().endswith('<text>'):
            preds.append(model.predict(source))

    csv_name = game_id + '.csv'
    with open(csv_name, 'w') as fp:
        cur_pred_ind = 0
        my_writer = writer(fp)
        my_writer.writerow(['Type', 'Player name', 'Action', 'Prediction'])
        full_text = sample_list[-1][0] + sample_list[-1][1]
        text_parts = full_text.split('<')

        in_phase_change = False
        cur_player = None
        for cur_part in text_parts:
            if len(cur_part) == 0:
                continue
            elif cur_part.startswith('phase change'):
                in_phase_change = True
                assert 'Daytime' in cur_part
            elif cur_part.startswith('victim'):
                victim_name = cur_part.split('> ')[1]
                my_writer.writerow(['victim', victim_name, '', ''])
                in_phase_change = False
            elif in_phase_change:
                assert False
            elif cur_part.startswith('player name'):
                cur_player = cur_part.split('> ')[1].strip()
            elif cur_part.startswith('text'):
                text = cur_part.split('> ')[1]
                my_writer.writerow(['text', cur_player, text, preds[cur_pred_ind]])
                cur_pred_ind += 1
                cur_player = None
            elif cur_part.startswith('vote'):
                vote = cur_part.split('> ')[1]
                my_writer.writerow(['vote', cur_player, vote, ''])
                cur_player = None
            elif cur_player is not None:
                assert False
    
