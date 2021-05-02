#import and db

#tables and routes

# @app.route('/search', methods =["GET", "POST"]) 
# def search():
#     search_val = request.form.get("search")

#     series_id = db.execute('DECLARE id_s NUMBER; BEGIN id_s:=search_by_name(":series_title"); dbms_output.put_line(id_s); END;', {'series_title':request.POST['search']})
#     post = db.session.query(series).filter_by(series_id=id).first()
#     return render_template('post.html', post=post)    

from flaskpost import app

if __name__ == '__main__':
    app.run(debug=True)