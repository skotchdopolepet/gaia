myGeometry <- "POLYGON ((32.913569 70.959697, 25.880466 71.691293, 14.100019 70.199994, 6.539434 65.366837, 2.319572 61.185625, -6.999289 59.534318, -12.977427 52.696361, -2.779427 45.58329, -11.922461 43.961191, -9.988358 36.879621, -2.779427 36.031332, 5.660296 38.272689, 11.286778 38.548165, 16.91326 34.885931, 30.451983 43.325178, 22.71557 53.852527, 29.572845 57.04073, 30.451983 69.900118, 32.913569 70.959697))"
myGeometry <- gsub("\n", "", myGeometry)
dateStart <- as.Date("2024-01-01")
dateEnd <- as.Date("2025-05-23")
species <- "Martes martes"
dailyLimit <- 10000

# Zoznam stĺpcov, ktoré chceme extrahovať
columns <- c(
  "eventDate",
  "dateIdentified",
  "latitude",
  "longitude",
  "kingdom",
  "class",
  "family",
  "genus",
  "species",
  "license",
  "behavior",
  "coordinateUncertaintyInMeters"
)

# Načítanie dát zo spocc
raw_data <- spocc::occ(
  query = species,
  from = "gbif",
  has_coords = TRUE,
  limit = dailyLimit,
  date = as.character(c(dateStart, dateEnd)),
  geometry = myGeometry
)$gbif$data

# Prevod listu na tibble a výber stĺpcov
spoccurrences <- raw_data |>
  purrr::list_rbind() |>
  dplyr::as_tibble()

# Ak existujú nejaké dáta, filtruj a uprav výstup
if (nrow(spoccurrences) > 0) {
  spoccurrences <- spoccurrences |>
    dplyr::select(tidyselect::any_of(columns)) |>
    dplyr::rename(
      decimalLatitude = latitude,
      decimalLongitude = longitude
    ) |>
    dplyr::filter(!is.na(eventDate)) |>
    dplyr::arrange(eventDate)
}

# ✅ Úprava, filtrovanie a zoradenie
if (nrow(spoccurrences) > 0) {
  # 🔍 Rýchla kontrola
  print(head(spoccurrences, 5))
  print(str(spoccurrences))
  # 💾 Export do CSV
  write.csv(spoccurrences, "Martes_2024-2025.csv", row.names = FALSE)
  
  print("✅ Export completed successfully.")
} else {
  print("⚠️ No data found in the specified area and time range.")
}