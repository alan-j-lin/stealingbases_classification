## Domain

For Project McNulty I decided to focus on the domain of sports, specifically baseball.
I am trying to predict whether or not a stolen base would be successful.

In terms of domain knowledge, I have watched baseball growing up and familiar with
the rules and teams in the MLB.

## Data

My current [dataset] is from Google Cloud's BigQuery public datasets. In that library
there is a dataset containing every single play from the 2016 MLB season. There are
in total 145 features and 762,000 entries. I would then have to subset the data to
only examine plays that involved a player trying to steal a base. When doing so I am left with
about 2000 events. Some specific features that I feel would be relevant are:

|   Feature            | Variable Type |
| :---------:          | :-----------: |
| Description          | String        |
| Inning Number        | Integer       |
| Outcome ID           | String        |
| Pitch Type           | String        |
| Pitch Speed          | Integer       |
| Pitch Zone           | Integer       |
| Pitcher Pitch Count  | Integer       |
| Hitter Pitch Count   | Integer       |
| Is Wild Pitch        | Integer       |
| Balls                | Integer       |
| Strikes              | Integer       |

With these numeric and categorical variables, I feel like these would be a good set of starting
features to examine to start predicting whether or not a stolen base would be successful.

[dataset]: https://www.kaggle.com/sportradar/baseball

## Known Unknowns:

A list of some currently known unknowns:

* No individual player statistics, if those are important then I would need to find a data sources
to join with. Would be interested in individual base running and opposing pitcher statistics
from the previous season (2015).
* Unsure if current amount of base stealing events is enough to form an accurate prediction,
may need to include pickoff events or try to find data from additional seasons.
* If I can get information regarding defensive shifts that could be a useful feature.
May instead try using preceding events as a proxy for that.
