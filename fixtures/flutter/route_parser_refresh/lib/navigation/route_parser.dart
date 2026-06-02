sealed class AppRoute {
  const AppRoute();
}

class HomeRoute extends AppRoute {
  const HomeRoute();
}

class ItemRoute extends AppRoute {
  const ItemRoute(this.id);
  final String id;
}

AppRoute parseRoute(String location) {
  if (location.startsWith('/item/')) {
    return ItemRoute(location.split('/').last);
  }
  return const HomeRoute();
}
