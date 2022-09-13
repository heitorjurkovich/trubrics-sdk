import pytest

from trubrics.exceptions import ClassifierNotSupportedError


def test__validate_single_edge_case(data_context, validator_classifier):
    edge_case_data = data_context.testing_data.iloc[0].to_dict()
    desired_output = 1

    result = validator_classifier._validate_single_edge_case(edge_case_data, desired_output)
    actual = True, {"prediction": 1}

    assert result == actual


@pytest.mark.parametrize(
    "kwargs,error_type",
    [
        ({"lower_output": 1, "upper_output": 1}, ValueError),
        ({"lower_output": 1, "upper_output": 3}, ClassifierNotSupportedError),
    ],
)
def test__validate_single_edge_case_in_range_raises(data_context, validator_classifier, kwargs, error_type):
    with pytest.raises(error_type):
        edge_case_data = data_context.testing_data.iloc[0].to_dict()
        validator_classifier._validate_single_edge_case_in_range(edge_case_data, **kwargs)


def test__validate_performance_against_threshold(validator_classifier):
    result = validator_classifier._validate_performance_against_threshold(metric="accuracy", threshold=0.7)
    actual = False, {"performance": 0.5}
    assert result == actual


def test__validate_biased_performance_across_category(validator_classifier):
    result = validator_classifier._validate_biased_performance_across_category(
        metric="accuracy", category="Sex", threshold=0.2
    )
    actual = False, {"max_performance_difference": 0.6}
    assert result == actual


def test__validate_performance_against_dummy(validator_classifier):
    result = validator_classifier._validate_performance_against_dummy(metric="accuracy", strategy="most_frequent")
    result[1]["dummy_performance"] = round(result[1]["dummy_performance"], 2)

    actual = False, {"dummy_performance": 0.67, "test_performance": 0.5}
    assert result == actual


def test__validate_feature_in_top_n_important_features(validator_classifier, feature_importance):
    result = validator_classifier._validate_feature_in_top_n_important_features(
        feature="Age", feature_importance=feature_importance, top_n_features=2
    )
    actual = True, {"feature_importance_ranking": 1}
    assert result == actual
