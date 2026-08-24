{
  description = "Lean companion for integral secant distributions";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [ elan git curl cacert gmp zlib coreutils ];
        NIX_LD = "${pkgs.glibc}/lib/ld-linux-x86-64.so.2";
        NIX_LD_LIBRARY_PATH =
          pkgs.lib.makeLibraryPath (with pkgs; [ stdenv.cc.cc.lib gmp zlib glibc ]);
        shellHook = ''
          export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export CURL_CA_BUNDLE="$SSL_CERT_FILE"
          export GIT_SSL_CAINFO="$SSL_CERT_FILE"
        '';
      };
    };
}
