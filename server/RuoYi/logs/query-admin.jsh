String url = "jdbc:mysql://47.105.65.4:13306/ry?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8";
try (var conn = java.sql.DriverManager.getConnection(url, "dbuser", "SecurePass2024");
     var stmt = conn.createStatement();
     var rs = stmt.executeQuery("select user_id, login_name, password, salt, status, del_flag from sys_user where login_name='admin'")) {
    while (rs.next()) {
        System.out.println(rs.getLong("user_id") + "|" + rs.getString("login_name") + "|" + rs.getString("password") + "|" + rs.getString("salt") + "|" + rs.getString("status") + "|" + rs.getString("del_flag"));
    }
}
/exit