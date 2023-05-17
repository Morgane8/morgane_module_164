"""Gestion des "routes" FLASK et des données pour les genres.
Fichier : gestion_disc_crud.py
Auteur : OM 2021.03.16
"""
from pathlib import Path

from flask import redirect
from flask import request
from flask import session
from flask import url_for

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.erreurs.exceptions import *
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFAjouterGenres
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFDeleteGenre
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFUpdateGenre

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /disc_afficher
    
    Test : ex : http://127.0.0.1:5575/disc_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_disc_sel = 0 >> tous les genres.
                id_disc_sel = "n" affiche le genre dont l'id est "n"
"""


@app.route("/disc_afficher/<string:order_by>/<int:id_disc_sel>", methods=['GET', 'POST'])
def disc_afficher(order_by, id_disc_sel):
    if request.method == "GET":
        try:
            with DBconnection() as mc_afficher:
                if order_by == "ASC" and id_disc_sel == 0:
                    strsql_disc_afficher = """SELECT * FROM t_disc"""
                    mc_afficher.execute(strsql_disc_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_genre"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_id_disc_selected_dictionnaire = {"value_id_disc_selected": id_disc_sel}
                    strsql_person_afficher = """SELECT *  FROM t_disc WHERE id_disc = %(value_id_disc_selected)s"""

                    mc_afficher.execute(strsql_person_afficher, valeur_id_disc_selected_dictionnaire)
                else:
                    strsql_disc_afficher = """SELECT * FROM t_disc"""

                    mc_afficher.execute(strsql_disc_afficher)

                data_disc = mc_afficher.fetchall()

                print("data_genres ", data_disc, " Type : ", type(data_disc))

                # Différencier les messages si la table est vide.
                if not data_disc and id_disc_sel == 0:
                    flash("""La table "t_person" est vide. !!""", "warning")
                elif not data_disc and id_disc_sel > 0:
                    # Si l'utilisateur change l'id_genre dans l'URL et que le genre n'existe pas,
                    flash(f"La personne demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_person" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données genres affichés !!", "success")

        except Exception as Exception_genres_afficher:
            raise ExceptionGenresAfficher(f"fichier : {Path(__file__).name}  ;  "
                                          f"{disc_afficher.__name__} ; "
                                          f"{Exception_genres_afficher}")

    # Envoie la page "HTML" au serveur.
    return render_template("disc/disc_afficher.html", data=data_disc)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /disc_ajouter
    
    Test : ex : http://127.0.0.1:5575/disc_ajouter
    
    Paramètres : sans
    
    But : Ajouter un genre pour un film
    
    Remarque :  Dans le champ "name_genre_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/disc_ajouter", methods=['GET', 'POST'])
def disc_ajouter_wtf():
    form = FormWTFAjouterGenres()
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                name_genre_wtf = form.nom_genre_wtf.data
                last_name_genre = name_genre_wtf.lower()
                first_name_pers = form.prenom_pers_wtf.data
                birth_date_pers = form.birth_date_pers_wtf.data
                gender_pers = form.gender_pers_wtf.data
                nationality_pers = form.nationality_pers_wtf.data
                valeurs_insertion_dictionnaire = {"value_last_name_pers": last_name_genre,
                                                  "value_first_name_pers": first_name_pers,
                                                  "value_birth_date_pers": birth_date_pers,
                                                  "value_gender_pers": gender_pers,
                                                  "value_nationality_pers": nationality_pers}
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert_person = """INSERT INTO t_disc (id_disc,last_name_pers,first_name_pers, birth_date_pers, gender_pers, nationality_pers) VALUES (NULL,%(value_last_name_pers)s,%(value_first_name_pers)s,%(value_birth_date_pers)s, %(value_gender_pers)s, %(value_nationality_pers)s) """
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(strsql_insert_person, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('disc_afficher', order_by='DESC', id_disc_sel=0))

        except Exception as Exception_genres_ajouter_wtf:
            raise ExceptionGenresAjouterWtf(f"fichier : {Path(__file__).name}  ;  "
                                            f"{disc_ajouter_wtf.__name__} ; "
                                            f"{Exception_genres_ajouter_wtf}")

    return render_template("genres/disc_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update
    
    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"
    
    Paramètres : sans
    
    But : Editer(update) un genre qui a été sélectionné dans le formulaire "disc_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_update_wtf" du formulaire "genres/disc_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/disc_update", methods=['GET', 'POST'])
def disc_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_genre"
    id_person_update = request.values['id_genre_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateGenre()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "disc_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            last_name_pers_update = form_update.nom_genre_update_wtf.data
            last_name_pers_update = last_name_pers_update.lower()
            first_name_pers_update = form_update.prenom_pers_update_wtf.data
            birth_date_pers_update = form_update.birth_date_pers_update_wtf.data
            gender_pers_update = form_update.gender_pers_update_wtf.data
            nationality_pers_update = form_update.nationality_pers_update_wtf.data

            valeur_update_dictionnaire = {"value_id_person": id_person_update,
                                          "value_last_name_pers_update": last_name_pers_update,
                                          "value_first_name_pers_update": first_name_pers_update,
                                          "value_birth_date_pers_update": birth_date_pers_update,
                                          "value_gender_pers_update": gender_pers_update,
                                          "value_nationality_pers_update": nationality_pers_update
                                          }
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_intitulegenre = """UPDATE t_person SET last_name_pers = %(value_last_name_pers_update)s, 
            first_name_pers = %(value_first_name_pers_update)s, birth_date_pers = %(value_birth_date_pers_update)s, 
            gender_pers = %(value_gender_pers_update)s, nationality_pers = %(value_nationality_pers_update)s WHERE id_person = %(value_id_person)s """
            with DBconnection() as mconn_bd:
                mconn_bd.execute(str_sql_update_intitulegenre, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_genre_update"
            return redirect(url_for('disc_afficher', order_by="ASC", id_disc_sel=id_person_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
            str_sql_id_genre = "SELECT * FROM t_disc " \
                               "WHERE id_disc = %(value_id_person)s"
            valeur_select_dictionnaire = {"value_id_person": id_person_update}
            with DBconnection() as mybd_conn:
                mybd_conn.execute(str_sql_id_genre, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_nom_genre = mybd_conn.fetchone()
            print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                  data_nom_genre["last_name_pers"])

            # Afficher la valeur sélectionnée dans les champs du formulaire "disc_update_wtf.html"
            form_update.nom_genre_update_wtf.data = data_nom_genre["last_name_pers"]
            form_update.prenom_pers_update_wtf.data = data_nom_genre["first_name_pers"]
            form_update.birth_date_pers_update_wtf.data = data_nom_genre["birth_date_pers"]
            form_update.gender_pers_update_wtf.data = data_nom_genre["gender_pers"]
            form_update.nationality_pers_update_wtf.data = data_nom_genre["nationality_pers"]

    except Exception as Exception_genre_update_wtf:
        raise ExceptionGenreUpdateWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{disc_update_wtf.__name__} ; "
                                      f"{Exception_genre_update_wtf}")

    return render_template("disc/disc_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete
    
    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"
    
    Paramètres : sans
    
    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "disc_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_delete_wtf" du formulaire "genres/disc_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@app.route("/disc_delete", methods=['GET', 'POST'])
def disc_delete_wtf():
    data_films_attribue_genre_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_genre"
    id_genre_delete = request.values['id_genre_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteGenre()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("disc_afficher", order_by="ASC", id_disc_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/disc_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_genre_delete = session['data_films_attribue_genre_delete']
                print("data_films_attribue_genre_delete ", data_films_attribue_genre_delete)

                flash(f"Effacer le genre de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_id_genre": id_genre_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_films_genre = """DELETE FROM t_genre_film WHERE fk_genre = %(value_id_person)s"""
                str_sql_delete_idgenre = """DELETE FROM t_person WHERE id_person = %(value_id_person)s"""
                # Manière brutale d'effacer d'abord la "fk_genre", même si elle n'existe pas dans la "t_genre_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "t_genre_film"
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    mconn_bd.execute(str_sql_delete_idgenre, valeur_delete_dictionnaire)

                flash(f"Genre définitivement effacé !!", "success")
                print(f"Genre définitivement effacé !!")

                # afficher les données
                return redirect(url_for('disc_afficher', order_by="ASC", id_disc_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_id_genre": id_genre_delete}
            print(id_genre_delete, type(id_genre_delete))

            # Requête qui affiche tous les films_genres qui ont le genre que l'utilisateur veut effacer
            str_sql_genres_films_delete = """SELECT id_genre_film, nom_film, id_genre, intitule_genre FROM t_genre_film 
                                            INNER JOIN t_film ON t_genre_film.fk_film = t_film.id_film
                                            INNER JOIN t_person ON t_genre_film.fk_genre = t_person.id_person
                                            WHERE fk_genre = %(value_id_person)s"""

            with DBconnection() as mydb_conn:
                mydb_conn.execute(str_sql_genres_films_delete, valeur_select_dictionnaire)
                data_films_attribue_genre_delete = mydb_conn.fetchall()
                print("data_films_attribue_genre_delete...", data_films_attribue_genre_delete)

                # Nécessaire pour mémoriser les données afin d'afficher à nouveau
                # le formulaire "genres/disc_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                session['data_films_attribue_genre_delete'] = data_films_attribue_genre_delete

                # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
                str_sql_id_genre = "SELECT * FROM t_disc WHERE id_disc = %(value_id_genre)s"

                mydb_conn.execute(str_sql_id_genre, valeur_select_dictionnaire)
                # Une seule valeur est suffisante "fetchone()",
                # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
                data_nom_genre = mydb_conn.fetchone()
                print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                      data_nom_genre["intitule_genre"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "disc_delete_wtf.html"
            form_delete.nom_genre_delete_wtf.data = data_nom_genre["intitule_genre"]

            # Le bouton pour l'action "DELETE" dans le form. "disc_delete_wtf.html" est caché.
            btn_submit_del = False

    except Exception as Exception_genre_delete_wtf:
        raise ExceptionGenreDeleteWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{disc_delete_wtf.__name__} ; "
                                      f"{Exception_genre_delete_wtf}")

    return render_template("disc/disc_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_films_associes=data_films_attribue_genre_delete)