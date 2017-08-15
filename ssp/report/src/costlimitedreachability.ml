open Gauss_pivot

(* exemple 2.10 *)

let a =
  [|
    [|1.; -1./.5.|];
    [|0.; 1.|]
  |]

let b = [| 1./.10.; 1./.5.|]

let x = resolve a b

let () =
  Array.iter (fun s -> Printf.printf "%.15F " s) x;
  Printf.printf "\n"
