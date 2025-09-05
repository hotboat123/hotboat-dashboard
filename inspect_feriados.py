import inputs_simulacion as cfg

print("Pais:", cfg.pais_festivos)
print("Anios:", getattr(cfg, 'feriados_anos', []))
cl = getattr(cfg, 'feriados_chile', [])
ar = getattr(cfg, 'feriados_argentina', [])
print("CL total:", len(cl))
print("AR total:", len(ar))
print("CL sample:", cl[:10])
print("AR sample:", ar[:10])

