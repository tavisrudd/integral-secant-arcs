{
  description = "Pinned toolchain for Integral Secant Distributions and Improved Bounds for Complete (k,n)-Arcs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          packages = with pkgs; [ python3 texlive.combined.scheme-full git coreutils ];
        in {
          default = pkgs.mkShell { inherit packages; };
          manuscript = pkgs.mkShell { inherit packages; };
        });
    };
}
