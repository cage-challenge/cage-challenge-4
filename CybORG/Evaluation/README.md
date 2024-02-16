# Getting Started

Welcome to CAGE Challenge 4!

This guide is intended to direct you to the necessary documentation for working with CybORG
and provides information on how to prepare your code for submission. Please be sure to read
through this document in its entirety prior to starting development to make sure you are
aware of the submission requirements.

## Where to get started

1. Download the CybORG package provided with the challenge or download the [repository](https://github.com/cage-challenge/cage-challenge-4).
2. Read through the CybORG README, also available on the 'Challenge Details' tab of the documentation.
3. Read the [Tutorials](/pages/how-to-guides/) to get a better understanding of CybORG and how to train agents using it.
4. Explore the [Reference](/pages/reference/reference/) section for more in-depth class explanations.
5. Develop your agents!

## Preparing a submission

Now that your agent has been developed and trained, it's time to get it ready for submission.
Submissions are uploaded as zip files containing a `submission.py` file, any model weights,
and your agent code that loads the model (if applicable).

To get started, create and move to a staging directory using `mkdir staging; cd staging`.

Submissions for this challenge must adhere to the following outline:

```
from CybORG import CybORG
from CybORG.Agents import BaseAgent

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from CybORG.Agents.Wrappers.EnterpriseMAE import EnterpriseMAE

### Import custom agents here ###
from dummy_agent import DummyAgent


class Submission:

    # Submission name
    NAME: str = "SUBMISSION NAME"

    # Name of your team
    TEAM: str = "TEAM NAME"

    # What is the name of the technique used? (e.g. Masked PPO)
    TECHNIQUE: str = "TECHNIQUE NAME"

    # Use this function to define your agents.
    AGENTS: dict[str, BaseAgent] = {
        f"blue_agent_{agent}": DummyAgent() for agent in range(5)
    }

    # Use this function to optionally wrap CybORG with your custom wrapper(s).
    def wrap(env: CybORG) -> MultiAgentEnv:
        return EnterpriseMAE(env)

```

Copy this template to your staging directory as `submission.py` and modify the value of
each field to reflect your submission. Agent code can be included directly in this file
or be copied to the staging directory and be imported by name.

As seen in the submission template, your custom agents and wrappers *must* conform to the
`BaseAgent` and `MultiAgentEnv` types, respectively. Please keep this in mind during
development.

#### Tip for loading weights from file

If your agent is a trained model with weights, include a copy of these weights in the
staging directory. Your agent code should load these weights from file using a relative
path: `load_weights(os.path.dirname(__file__) + "/agent_weights.pkl")`.

### Testing your submission

To verify that your agent and associated wrappers will be properly picked up by the evaluation
script, test your submission using the evaluation script provided with CybORG:
`python3 -m CybORG.Evaluation.evaluation --max-eps 2 /path/to/staging /tmp/output`.
The standard output from this command should closely resemble the following output:

```
CybORG v3.1, Scenario4
Author: SUBMISSION NAME, Team: TEAM NAME, Technique: TECHNIQUE NAME
Using agents {'blue_agent_0': DummyAgent, 'blue_agent_1': DummyAgent, 'blue_agent_2': DummyAgent, 'blue_agent_3': DummyAgent, 'blue_agent_4': DummyAgent}, if this is incorrect please update the code to load in your agent
Results will be saved to /tmp/output/
Average reward is: -18386 with a standard deviation of 2904.794657114337
File took 0:01:33.236403 amount of time to finish evaluation
Saving results to /tmp/output/
```

### Packaging and submitting

The last step before packaging is to create an empty `metadata` file using `touch metadata`.
This ensures CodaLabs will treat the submission as a code submission and will be forwarded
to the evaluation script. It is imperative that this `metadata` file is empty.

Finally, all the files in the staging directory can be packaged into a zip file for
submission using `zip ../name_of_your_submission.zip *`. If you are using a graphical zip
utility, ensure that only the files within the `staging` directory and not the directory
itself are included in the zip file. The final package should be similar to the following:

```
name_of_your_submission.zip
├ metadata
├ submission.py
├ agent_code.py
└ agent_weights.pkl
```

Once the package contents have been verified, upload the zip file to the competition and
verify that the submission status is `running`. At this point, the evaluation process can
take up to several hours, so be sure to check back periodically to ensure that the process
has not failed.


## Additional information

### Description of approach

As part of your submission, we request that you share a description of the methods/techniques
used in developing your agents. We will use this information as part of our in-depth analysis
and comparison of the various techniques submitted to the challenge. In hosting the CAGE
challenges, one of our main goals is to understand the techniques that lead to effective
autonomous cyber defensive agents, as well as those that are not as effective. We are
planning on publishing the analysis and taxonomy of the different approaches that create
autonomous cyber defensive agents. To that end, we encourage you to also share details on
any unsuccessful approaches taken. Please also feel free to share any interesting discoveries
and thoughts regarding future work to help us shape the future of the CAGE Challenges.

We provide a latex template as a guide for writing your description.
An examplar description can be found here.

We provide a [latex template](https://github.com/cage-challenge/CybORG/blob/main/CybORG/Evaluation/submission/submission_template_example/template_readme.md) as a guide for writing your description.
An examplar description can be found [here](https://arxiv.org/pdf/2211.15557.pdf).


### Evaluation results

If you have run the evaluation script locally, please feel free to include your results
as part of the submission in an `evaluation_output` directory in your submission zip file.

To run the evaluation locally, use
`python3 -m CybORG.Evaluation.evaluation /path/to/staging /path/to/staging/evaluation_output`.

### Issues

If you have any questions or encounter an error, please submit an issue on the challenge forum
on CodaLabs. In the case of an error, please provide a detailed description of the circumstances
surrounding the error and the full output where possible so that we can replicate the error.
