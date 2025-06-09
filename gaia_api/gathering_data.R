# ── packages ───────────────────────────────────────────────────────────────────
# install.packages(c("spocc","dplyr","purrr","lubridate","readr","stringr"))
library(spocc)
library(dplyr)
library(purrr)
library(lubridate)
library(readr)      # for write_csv()
library(stringr)    # for str_squish()

# ── user parameters ────────────────────────────────────────────────────────────
myGeometry <- "
  POLYGON (
    (10.537296 58.170702, 4.738046 56.704506, -4.839504 50.569283,
     -7.03619 48.04871, -2.818553 44.402392, -10.375153 44.402392,
     -11.956766 39.504041, -9.496478 35.603719, -3.082156 35.960223,
      3.507902 37.996163, 9.658622 38.479395, 14.403463 39.368279,
     17.742426 44.024422, 19.851244 47.754098, 16.424414 54.007769,
     10.537296 58.170702
    )
  )
"
# collapse to one line, single spaces
myGeometry <- str_squish(myGeometry)

species    <- "Vespa velutina"
dailyLimit <- 10000

# columns we want to keep (as they come from GBIF)
keep_cols <- c(
  "eventDate", "dateIdentified",
  "decimalLatitude", "decimalLongitude",
  "kingdom", "class", "family",
  "genus", "species", "license",
  "behavior", "coordinateUncertaintyInMeters"
)

# ── build the quarter table ────────────────────────────────────────────────────
start_dates <- seq.Date(
  from = as.Date("2010-01-01"),
  to   = as.Date("2024-10-01"),  # last quarter start
  by   = "quarter"
)

end_dates <- c(
  start_dates[-1] - days(1),
  as.Date("2024-12-31")
)

quarters_tbl <- tibble(start = start_dates, end = end_dates)

# ── fetch GBIF data quarter-by-quarter ─────────────────────────────────────────
all_occurrences <- quarters_tbl %>%
  mutate(data = map2(start, end, ~ {
    message("→ querying ", .x, " to ", .y)
    # fetch and bind rows in one go
    occ(
      query      = species,
      from       = "gbif",
      has_coords = TRUE,
      limit      = dailyLimit,
      date       = as.character(c(.x, .y)),
      geometry   = myGeometry
    )$gbif$data %>%
      bind_rows()
  })) %>%
  pull(data) %>%         # extract the list of data‐frames
  bind_rows() %>%        # bind all quarters together
  as_tibble() %>%        # ensure tibble
  select(any_of(keep_cols)) %>%  # keep only the columns we want
  rename(
    latitude  = decimalLatitude,
    longitude = decimalLongitude
  ) %>%
  filter(!is.na(eventDate)) %>%  # drop records missing the date
  arrange(eventDate)

# ── export ─────────────────────────────────────────────────────────────────────
# use a plain ASCII hyphen in the filename
write_csv(
  all_occurrences,
  "vespa_velutina_gbif_2010-2024.csv"
)

# Optional: also save as RDS or Parquet
# write_rds(all_occurrences,    "vespa_velutina_gbif_2010-2024.rds")
# arrow::write_parquet(all_occurrences, "vespa_velutina_gbif_2010-2024.parquet")

# return the tibble
all_occurrences