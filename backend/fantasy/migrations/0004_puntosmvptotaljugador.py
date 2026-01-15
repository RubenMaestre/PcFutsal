# Generated manually for PuntosMVPTotalJugador model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0003_puntosmvpjornada'),
        ('jugadores', '0001_initial'),
        ('nucleo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuntosMVPTotalJugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntos_base_total', models.FloatField(default=0.0)),
                ('puntos_con_coef_total', models.FloatField(default=0.0)),
                ('goles_total', models.IntegerField(default=0)),
                ('partidos_total', models.IntegerField(default=0)),
                ('ultima_jornada_procesada', models.IntegerField(default=0)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos_mvp_total', to='jugadores.jugador')),
                ('temporada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos_mvp_total', to='nucleo.temporada')),
            ],
            options={
                'ordering': ['-temporada', '-puntos_con_coef_total'],
            },
        ),
        migrations.AddIndex(
            model_name='puntosmvptotaljugador',
            index=models.Index(fields=['temporada', '-puntos_con_coef_total'], name='fantasy_pun_tempora_ranking_idx'),
        ),
        migrations.AddIndex(
            model_name='puntosmvptotaljugador',
            index=models.Index(fields=['jugador', 'temporada'], name='fantasy_pun_jugador_temp_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='puntosmvptotaljugador',
            unique_together={('jugador', 'temporada')},
        ),
    ]




