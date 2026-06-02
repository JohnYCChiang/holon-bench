import '../services/user_api.dart';

class UserController {
  UserController(this.api);

  final UserApi api;

  Future<String> load() {
    return api.fetchUser();
  }

  Future<String> refresh() {
    return api.fetchUser();
  }
}
