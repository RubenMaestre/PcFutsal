# Generated manually for PuntosMVPJornada model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0002_initial'),
        ('jugadores', '0001_initial'),
        ('nucleo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuntosMVPJornada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jornada', models.IntegerField()),
                ('puntos_base', models.FloatField(default=0.0)),
                ('puntos_con_coef', models.FloatField(default=0.0)),
                ('coef_division', models.FloatField(default=1.0)),
                ('partidos_jugados', models.IntegerField(default=0)),
                ('goles', models.IntegerField(default=0)),
                ('fecha_calculo', models.DateTimeField(auto_now=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos_mvp_jornada', to='nucleo.grupo')),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos_mvp_jornada', to='jugadores.jugador')),
                ('temporada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos_mvp_jornada', to='nucleo.temporada')),
            ],
            options={
                'ordering': ['-temporada', '-jornada', '-puntos_con_coef'],
            },
        ),
        migrations.AddIndex(
            model_name='puntosmvpjornada',
            index=models.Index(fields=['jugador', 'temporada'], name='fantasy_pun_jugador_7a8b2d_idx'),
        ),
        migrations.AddIndex(
            model_name='puntosmvpjornada',
            index=models.Index(fields=['temporada', 'grupo', 'jornada'], name='fantasy_pun_tempora_8c9d3e_idx'),
        ),
        migrations.AddIndex(
            model_name='puntosmvpjornada',
            index=models.Index(fields=['temporada', 'jornada'], name='fantasy_pun_tempora_9d4e5f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='puntosmvpjornada',
            unique_together={('jugador', 'temporada', 'grupo', 'jornada')},
        ),
    ]




