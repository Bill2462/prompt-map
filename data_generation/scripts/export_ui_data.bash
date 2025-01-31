OUT_DIR="/netscratch/adamkiewicz/prompt_gen/ui_data"
IN_DIR="/netscratch/adamkiewicz/prompt_gen/run"

mkdir -p $OUT_DIR

cp -r -v $IN_DIR/embeddings $OUT_DIR/embeddings_for_search
cp -v $IN_DIR/db.parquet $OUT_DIR/db.parquet
cp -r -v $IN_DIR/intermidiate_stages/6/reduced_embeds $OUT_DIR/map_positions

mkdir -p $OUT_DIR/map_labels
cp -r -v $IN_DIR/intermidiate_stages/6/map_labels $OUT_DIR/map_labels/lvl_!
cp -r -v $IN_DIR/intermidiate_stages/7/map_labels $OUT_DIR/map_labels/lvl_2
