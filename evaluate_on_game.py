from csv import writer
from train.demonstrate import load_game_from_csv, Demonstrator
from metrics.calc_metrics import calc_metrics
import sys
import torch

INSTRUCTION = "Complete the message in this Mafia game: "


def evaluate_on_game(dataset_path, game_id, max_source_length, model_path=None,
                     pretrained_model_name=None, pass_token_is_used=True):
    if model_path:
        model = Demonstrator(max_source_length=max_source_length, model_path=model_path)
    elif pretrained_model_name:
        model = Demonstrator(max_source_length=max_source_length,
                             pretrained_model_name=pretrained_model_name)
    else:
        raise ValueError("Missing either model_path or pretrained_model_name")
    sample_list = load_game_from_csv(dataset_path, game_id)
    sample_list.sort(key=lambda x: x[0].count('text') + x[0].count('vote'))

    preds = []
    predicted_players = []
    count = 1
    loss_sum = 0
    perplexity_sum = 0
    for source, target, player_name in sample_list:
        if source.strip().endswith('<text>'):
            if pretrained_model_name:
                source = INSTRUCTION + source
            with torch.no_grad():
                prediction = model.predict(source)
            preds.append((prediction, player_name))
            predicted_players.append(player_name)
            print('Prediction ' + str(count) + ': player "' + player_name + '" says "' + prediction + '"')
            cur_loss, cur_perplexity = calc_metrics(model.model, model.tokenizer, source, target,
                                                    max_source_length, model.special_token_ids,
                                                    model.model_name)
            loss_sum += cur_loss
            perplexity_sum += cur_perplexity
            count += 1
    print('Mean loss: ' + str(loss_sum/(count - 1)))
    print('Mean perplexity: ' + str(perplexity_sum/(count - 1)))
    predicted_players = {x: True for x in predicted_players}

    if pretrained_model_name:
        game_id = "without_fine_tune_" + game_id
    csv_name = game_id + '.csv'
    with open(csv_name, 'w') as fp:
        cur_pred_ind = 0
        my_writer = writer(fp)
        my_writer.writerow(['Type', 'Player name', 'Action', 'Prediction'])
        full_text = sample_list[-1][0] + sample_list[-1][1]
        text_parts = full_text.split('<')

        cur_player = None
        for cur_part in text_parts:
            if len(cur_part) == 0:
                continue
            elif cur_part.startswith('phase change'):
                assert 'Daytime' in cur_part or 'Nighttime' in cur_part
            elif cur_part.startswith('victim'):
                victim_name = cur_part.split('> ')[1]
                my_writer.writerow(['victim', victim_name, '', ''])
            elif cur_part.startswith('player name'):
                cur_player = cur_part.split('> ')[1].strip()
            elif cur_part.startswith('text'):
                text = cur_part.split('> ')[1]
                if text == '' and pass_token_is_used:
                    # it means that cur_part was originally from '...<text> <...'
                    # so cur_part == 'text> ' => currently can only mean it was '<text> <pass>'
                    text = '<pass>'
                if cur_player in predicted_players:
                    assert cur_player == preds[cur_pred_ind][1], 'Error: for prediction ' + str(cur_pred_ind+1) + ', current player name "' + cur_player + '" differs from recorded player name "' + preds[cur_pred_ind][1] + '"'
                    my_writer.writerow(['text', cur_player, text, preds[cur_pred_ind][0]])
                    cur_pred_ind += 1
                else:
                    my_writer.writerow(['text', cur_player, text, ''])
                cur_player = None
            elif cur_part.startswith('vote'):
                vote = cur_part.split('> ')[1]
                my_writer.writerow(['vote', cur_player, vote, ''])
                cur_player = None
            elif cur_part.startswith('voting history') or cur_part.startswith('mention history'):
                cur_player = None
            elif cur_player is not None:
                assert False


if __name__ == "__main__":
    evaluate_on_game(model_path=sys.argv[1], dataset_path=sys.argv[2], game_id=sys.argv[3],
                     max_source_length=int(sys.argv[4]))
