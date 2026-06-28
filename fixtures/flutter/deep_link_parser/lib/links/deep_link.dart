sealed class AppLink {
  const AppLink();
}

class HomeLink extends AppLink {
  const HomeLink();
}

class ProductLink extends AppLink {
  const ProductLink(this.id, {this.ref});
  final String id;
  final String? ref;
}

class ProfileLink extends AppLink {
  const ProfileLink(this.user);
  final String user;
}

class UnknownLink extends AppLink {
  const UnknownLink();
}

/// Parses `myapp://<host>/<segments>?<query>` deep links.
AppLink parseDeepLink(String raw) {
  final uri = Uri.parse(raw);
  if (uri.host == 'product') {
    return ProductLink(uri.pathSegments.first);
  }
  return const HomeLink();
}
