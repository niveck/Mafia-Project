from csv import writer

def evaluate_on_game(model, sample_list, player_name):
    assert sample_list[-1][0].count(player_name + ' <text>') + sample_list[-1][0].count(player_name + ' <vote>') == len(sample_list)
    preds = []
    for source, _ in sample_list:
        if source.strip().endswith('<test>'):
            preds.append(model.predict(source))

    with open(player_name + '.csv', 'w') as fp:
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
                cur_player = cur_part.split('> ')[1]
            elif cur_part.startswith('text'):
                text = cur_part.split('> ')[1]
                my_writer.writerow(['text', cur_player, text, preds[cur_pred_ind]])
                cur_pred_ind += 1
                cur_player = None
            elif cur_part.starswith('vote'):
                vote = cur_part.split('> ')[1]
                my_writer.writerow(['vote', cur_player, vote, ''])
                cur_player = None
            elif cur_player is not None:
                assert False
    
