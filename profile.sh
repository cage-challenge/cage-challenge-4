#!/bin/bash

# Define file name prefixes
TEST_FILE="CybORG/Tests/test_sim/test_Acceptance/test_cc4/test_heuristic_agents.py"
PROFILE_PREFIX="test_profile"
DOT_OUTPUT_PREFIX="dot_output"
SVG_OUTPUT_PREFIX="profile_graph"

echo "Run cProfile..."
python -m cProfile -o "${PROFILE_PREFIX}.pstats" -m pytest "${TEST_FILE}"

echo "Convert pstats to dot format..."
gprof2dot -f pstats "${PROFILE_PREFIX}.pstats" -o "${DOT_OUTPUT_PREFIX}_total.dot"
gprof2dot --color-nodes-by-selftime -f pstats "${PROFILE_PREFIX}.pstats" -o "${DOT_OUTPUT_PREFIX}_self.dot"

echo "Convert dot to SVG..."
dot -Tsvg "${DOT_OUTPUT_PREFIX}_total.dot" -o "${SVG_OUTPUT_PREFIX}_total.svg"
dot -Tsvg "${DOT_OUTPUT_PREFIX}_self.dot" -o "${SVG_OUTPUT_PREFIX}_self.svg"

echo "profiling done!"
